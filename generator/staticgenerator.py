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

    def __init__(self, dropboxPath, outputPath) :
        """
            Constructor: initialize with the absolute path to the
            Dropbox folder, output directory and relative path of the
            landing page.
        """
        self.dropboxPath = dropboxPath
        self.outputPath = outputPath
        
        self.BuildTree(dropboxPath)
        self.InitMeta()
        self.InitSections()


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
        self.sections = self.meta["page_order"]
        for idx in range(0,len(self.sections)) :
            if isinstance(self.sections[idx], unicode) == False :
                self.sections[idx] = self.sections[idx].decode(encoding='UTF-8')

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
                    if (contentType=="textContent") :
                        self.GenerateTextPage(directory.rstrip("/"),content)

    def GenerateHeaderNav(self,name) :
        headerNavTpl = self.GetTemplate("nav-header-element.tpl")
        substitutions = list()
        for section in self.sections :
            templateVariables = dict()
            if section == name.decode(encoding='UTF-8') :
                templateVariables["active"] = True
            if section == self.meta["landing_page"] :
                templateVariables["page_url"] = "index.html"
            else :
                templateVariables["page_url"] = section.rsplit(" ")[-1]+".html"
            templateVariables["page_name"] = section
            substitutions.append(headerNavTpl.render(templateVariables))
        return substitutions

    def GenerateHtmlPage(self,name,pageTemplate,substitutions) :
        # Generate html page
        if name != self.meta["landing_page"] :
            f = open(self.outputPath + name.rsplit(" ")[-1]  + ".html","w")
        else :
            f = open(self.outputPath + "index.html", "w")   
        f.write(pageTemplate.render(dict(substitutions.items()+self.meta.items())).encode('utf8'))
        f.close()

    def GeneratePicturePage(self,name,contentDictionary) :
        # Declare template variables
        substitutions = {"headerNav":[],"contentNav":[],"yearNav":[],"workList":[]}
        
        # fetch templates
        pageTemplate = self.GetTemplate("picture-page.tpl")
        navContentElementTemplate = self.GetTemplate("nav-content-element.tpl")
        pictureElementTemplate = self.GetTemplate("picture-element.tpl")

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
        substitutions["allNav"] = navContentElementTemplate.render({"category_url":"","category_name":"toutes"})
        for element in uniqueCategories :
            templateVariables = {"category_url":element, "category_name":element}
            substitutions["contentNav"].append(navContentElementTemplate.render(templateVariables))
        for element in uniqueYears :
            templateVariables = {"category_url":element, "category_name":element}
            substitutions["yearNav"].append(navContentElementTemplate.render(templateVariables))

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
            substitutions["workList"].append(pictureElementTemplate.render(templateVariables))

        # Generate html page
        self.GenerateHtmlPage(name,pageTemplate,substitutions)
    
        # Move files
        for element in contentDictionary["Files"] :
            shutil.copyfile(self.dropboxPath+name+"/"+element["path"],self.outputPath+"img/work/"+element["path"])
            shutil.copyfile(self.dropboxPath+name+"/"+element["path"],self.outputPath+"img/thumb/"+element["path"])

    def GenerateTextPage(self,name,contentDictionary) :
        # Declare template variables
        substitutions = dict()
        pageTemplate = self.GetTemplate("text-page.tpl")
        textImageTemplate = self.GetTemplate("text-image.tpl")
        textContentTemplate = self.GetTemplate("text-content.tpl")
        # Generate base navigation
        substitutions["headerNav"] = self.GenerateHeaderNav(name)
        
        # Check for special page token (currently defined: CONTACT_FORM)
        if contentDictionary["header"] == "CONTACT_FORM" :
            formContactTpl = self.GetTemplate("form-contact.tpl")
            substitutions["content_text"]=formContactTpl.render()
        # Default case
        else : 
            # Fetch image
            substitutions["content_image"] =  textImageTemplate.render({"image_url":contentDictionary["image"]})

            # Fetch text: render header, then content.
            text = textContentTemplate.render({"text_content":contentDictionary["header"].split("\n")}) 
            for section in contentDictionary["sections"] :
                templateVariables = {"text_section_title":section["name"], "text_content": section["content"].split("\n") }
                text = text+textContentTemplate.render(templateVariables)
            substitutions["content_text"] = text

        self.GenerateHtmlPage(name,pageTemplate,substitutions)

