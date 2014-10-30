#!/usr/bin/python

import jinja2
import os
import yaml
import time
import shutil
import logging

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
        self.InitMeta()
        self.InitSections()

        logging.basicConfig(filename='generator.log',level=logging.INFO, format='[%(levelname)s] %(asctime)s : %(message)s', datefmt='%d-%m-%y %H:%M:%S')


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

    def InitMeta(self) :
        f = open(self.dropboxPath+"metaContent.yml","r")
        self.meta = yaml.load(f.read())

    def InitSections(self) :
        # check that sections match the metaContent
        for directory in self.tree :
            strippedName = directory.rstrip("/").decode(encoding='UTF-8')
            if self.sections.count(strippedName)==0 and strippedName != "":
                if self.meta["page_order"].count(strippedName) > 0:
                    self.sections.append(strippedName)
        # Sort sections according to meta
        self.sections=self.meta["page_order"]


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

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Generators
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GenerateWebsite(self) :
        for directory in self.tree :
            for f in self.tree[directory]:
                path=self.dropboxPath+directory+f
                contentType, content = self.ReadFile(path)
                if content.get("Files") != None or content.get("header") != None :
                    if (contentType=="pictureContent") :
                        self.GeneratePicturePage(directory.rstrip("/"),content)
                        logging.info("Generated "+directory.rstrip("/")+" [pictureType]")
                    if (contentType=="textContent") :
                        self.GenerateTextPage(directory.rstrip("/"),content)
                        logging.info("Generated "+directory.rstrip("/")+" [textType]")

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
                templateVariables["page_url"] = section.rsplit(" ")[-1]+".html"
            templateVariables["page_name"] = section
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
        substitutions["allNav"] = contentNavTpl.render({"category_url":"","category_name":"toutes"})
        for element in uniqueCategories :
            templateVariables = {"category_url":element, "category_name":element}
            substitutions["contentNav"].append(contentNavTpl.render(templateVariables))
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
                                 "image_title":element["title"],
                                 "image_spec":element["spec"],
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

    def GenerateTextPage(self,name,contentDictionary) :
        # Declare template variables
        substitutions = {"headerNav":[],"contentNav":[],"yearNav":[],"workList":[]}
        
        # # fetch templates
        # pageTpl = self.GetTemplate("picture.tpl")
        # contentNavTpl = self.GetTemplate("nav-content-element.tpl")
        # pictureTpl = self.GetTemplate("picture-element.tpl")

        # # Generate base navigation
        # substitutions["headerNav"] = self.GenerateHeaderNav(name)

        # # Determine extra navigations
        # uniqueCategories = list()
        # uniqueYears = list()
        # for element in contentDictionary["Files"] :
        #     if uniqueCategories.count(element["category"]) == 0 :
        #         uniqueCategories.append(element["category"])
        #     if uniqueYears.count(element["year"]) == 0 :
        #         uniqueYears.append(element["year"])
        # # Generate extra navigations
        # substitutions["allNav"] = contentNavTpl.render({"category_url":"","category_name":"toutes"})
        # for element in uniqueCategories :
        #     templateVariables = {"category_url":element, "category_name":element}
        #     substitutions["contentNav"].append(contentNavTpl.render(templateVariables))
        # for element in uniqueYears :
        #     templateVariables = {"category_url":element, "category_name":element}
        #     substitutions["yearNav"].append(contentNavTpl.render(templateVariables))

        # # Determine workList
        # workList = list()
        # for element in contentDictionary["Files"] :
        #     workList.append(element)
        # # Generate workList
        # for element in contentDictionary["Files"] :
        #     templateVariables = {"category_name":element["category"],
        #                          "image_title":element["title"],
        #                          "image_spec":element["spec"],
        #                          "image_url":"img/work/"+element["path"],
        #                          "image_thumbnail_url":"img/thumb/"+element["path"],
        #                          "image_year":element["year"]}
        #     substitutions["workList"].append(pictureTpl.render(templateVariables))

        # # Generate html page
        # if name != self.landingPage :
        #     f = open(self.outputPath + name + ".html","w")
        # else :
        #     f = open(self.outputPath + "index.html", "w")   
        # f.write(pageTpl.render(dict(substitutions.items()+self.meta.items())).encode('utf8'))
        # f.close()

        # # Move files
        # for element in contentDictionary["Files"] :
        #     shutil.copyfile(self.dropboxPath+name+"/"+element["path"],self.outputPath+"img/work/"+element["path"])
        #     shutil.copyfile(self.dropboxPath+name+"/"+element["path"],self.outputPath+"img/thumb/"+element["path"])