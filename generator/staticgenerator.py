#!/usr/bin/python

import jinja2
import os
import yaml
import time
import shutil

class StaticGenerator :
    """
        Generate html content from a Dropbox folder.
    """

    # Data members
    tree=dict()
    meta=dict()

    dropboxPath=""
    outputPath=""
    
    sections=list()
    landingPage=""

    def __init__(self, dropboxPath, outputPath, landingPage) :
        """
            Constructor: initialize with the absolute path to the
            Dropbox folder, output directory and relative path of the
            landing page.
        """
        self.dropboxPath = dropboxPath
        self.outputPath = outputPath
        self.landingPage = landingPage
        
        self.BuildTree(dropboxPath)
        self.InitSections()
        self.InitMeta()


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializers
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildTree(self,filePath) :
        """ 
            Recursive directory tree builder.
        """
        contentList = os.listdir(filePath)
        fileList = []
        for content in contentList :
            path = os.path.join(filePath,content)
            if os.path.isdir(path) :
                self.BuildTree(path)
            else :
                fileList.append(content)
        self.tree[filePath[len(self.dropboxPath):]+"/"]=fileList

    def InitSections(self) :
        for directory in self.tree :
            strippedName = directory.rstrip("/")
            if self.sections.count(strippedName)==0 and strippedName != "":
                self.sections.append(strippedName)

    def InitMeta(self) :
        f = open(self.dropboxPath+"metaContent.yml","r")
        self.meta = yaml.load(f.read())


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Utilities
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ReadFile(self,filePath) :
        """ 
            Determine if a file contains YAML.
            If true, read and return content as a dictionary + file type.
        """
        directory, fileName = os.path.split(filePath)
        name, extension = os.path.splitext(fileName)

        if extension == ".yaml" or  extension == ".yml" :
            f = open(filePath,"r")
            return name, yaml.load(f.read())

        return name, { "Files":None } 

    def GetTemplate(self,templateName) :
        templateLoader = jinja2.FileSystemLoader(searchpath = "../templates") 
        env = jinja2.Environment( loader = templateLoader )
        return env.get_template( templateName )


    def SetupDirectory(self) :
        shutil.copytree("js",self.outputPath+"js")
        shutil.copytree("css",self.outputPath+"css")
        shutil.copytree("img",self.outputPath+"img")
        try : os.mkdir(self.outputPath+"img/work/")
        except OSError: pass
        try : os.mkdir(self.outputPath+"img/thumb/")
        except OSError: pass

        # Generate pages
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Generators
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GenerateWebsite(self) :
        # Setup directory
        self.SetupDirectory()

        for directory in self.tree :
            for f in self.tree[directory]:
                path=self.dropboxPath+directory+f
                contentType, content = self.ReadFile(path)
                if content.get("Files") != None or content.get("header") != None :
                    if (contentType=="pictureContent") :
                        self.GeneratePicturePage(directory.rstrip("/"),content)
                        print "[LOG] Generated "+directory.rstrip("/")+" on "+time.ctime()
                    # if (contentType=="textContent") :
                    #     self.GenerateTextPage(directory.rstrip("/"),content)



    def GenerateHeaderNav(self,name) :
        headerNavTpl = self.GetTemplate("nav-header-element.tpl")
        substitutions = list()
        for section in self.sections :
            templateVariables = dict()
            if section == name :
                templateVariables["active"] = True
            if section == self.landingPage :
                templateVariables["page_url"] = "index.html"
            else :
                templateVariables["page_url"] = section.decode(encoding='UTF-8').rsplit(" ")[-1]+".html"
            templateVariables["page_name"] = section.decode(encoding='UTF-8')
            substitutions.append(headerNavTpl.render(templateVariables))
        return substitutions

    def GeneratePicturePage(self,name,contentDictionary) :
        # Declare template variables
        substitutions = {"headerNav":[],"contentNav":[],"yearNav":[],"workList":[]}
        
        # fetch templates
        pageTpl = self.GetTemplate("picture.tpl")
        contentNavTpl = self.GetTemplate("nav-content-element.tpl")
        pictureTpl = self.GetTemplate("picture-element.tpl")

        # Generate base navigation
        substitutions["headerNav"] = self.GenerateHeaderNav(name)

        # Determine extra navigations
        uniqueCategories = list()
        uniqueYears = list()
        for element in contentDictionary["Files"] :
            if uniqueCategories.count(element["category"]) == 0 :
                uniqueCategories.append(element["category"])
            if uniqueYears.count(element["year"]) == 0 :
                uniqueYears.append(element["year"])
        # Generate extra navigations
        substitutions["contentNav"].append(contentNavTpl.render({"category_url":"","category_name":"toutes"}))
        for element in uniqueCategories :
            templateVariables = {"category_url":element, "category_name":element}
            substitutions["contentNav"].append(contentNavTpl.render(templateVariables))
        substitutions["yearNav"].append(contentNavTpl.render({"category_url":"","category_name":"toutes"}))
        for element in uniqueYears :
            templateVariables = {"category_url":element, "category_name":element}
            substitutions["yearNav"].append(contentNavTpl.render(templateVariables))

        # Determine workList
        workList = list()
        for element in contentDictionary["Files"] :
            workList.append(element)
        # Generate workList
        for element in contentDictionary["Files"] :
            templateVariables = {"category_name":element["category"],
                                 "image_titre":element["title"],
                                 "image_url":"img/work/"+element["path"],
                                 "image_thumbnail_url":"img/thumb/"+element["path"],
                                 "image_year":element["year"]}
            substitutions["workList"].append(pictureTpl.render(templateVariables))

        # Generate html page
        if name != self.landingPage :
            f = open(self.outputPath + name + ".html","w")
        else :
            f = open(self.outputPath + "index.html", "w")   
        f.write(pageTpl.render(dict(substitutions.items()+self.meta.items())).encode('utf8'))
        f.close()

        # Move files
        for element in contentDictionary["Files"] :
            shutil.copyfile(self.dropboxPath+name+"/"+element["path"],self.outputPath+"img/work/"+element["path"])
            shutil.copyfile(self.dropboxPath+name+"/"+element["path"],self.outputPath+"img/thumb/"+element["path"])

    def GenerateNavigation(self) :
        # Generate website sections from directory
        sectionUrls = dict()
        for topDirectory in self.tree :
            section = topDirectory.rsplit("/")[0]
            if sectionUrls.get(section)==None and section != "" :
                if section != self.landingPage :
                    sectionUrls[section] = self.outputPath + section + ".html"
                else :
                    sectionUrls[section] = self.outputPath + "index.html"

        return sectionUrls