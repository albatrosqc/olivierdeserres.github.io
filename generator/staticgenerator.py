#!/usr/bin/python
import jinja2
import yaml
import hashlib, os, shutil, logging
import pprint as pp

# Configure CointipBot logger
logging.basicConfig(filename='generator.log',level=logging.INFO, 
                    format='[%(levelname)s] %(asctime)s : %(message)s', datefmt='%d-%m-%y %H:%M:%S')
log = logging.getLogger("staticgenerator")

class Helper :
    ''' Small helper function that are useful for both StaticGenerator and FileManager. '''

    def __init__(self) :
        ''' Empty constructor; useful for direct usage within other classes'''
        log.debug("Helper.__init__(0)")

    def isYaml(self, filePath) :
        ''' 
            Override the default exception behavior of yaml.load(1) to turn it into a
            simple test of validity.
        '''
        log.debug("Helper.isYaml(1) with filePath="+filePath)

        try :
            yaml.load(open(filePath,"r").read())
            return True
        except yaml.YAMLError:
            return False

    def URLFromDirectory(self, directory, index="") :
        ''' 
            Define a unique correspondence between a directory name
            and a URL. Unified use of this functions enforce a unified 
            naming scheme.
            A directory that holds the content of the index is associated to
            'index.html' automatically.
        '''
        log.debug("Helper.URLFromDirectory(2) with directory="+directory+", index="+index)
        
        if (directory==index) :
            return "index.html"
        else :
            return directory.rsplit(" ")[-1]+".html"


class StaticGenerator :
    '''Generate HTML content from a source folder that follows the appropriate pattern.'''

    # Data members
    tree=dict()
    meta=dict()

    sourcePath=""
    outputPath=""
    
    sections=list()

    def __init__(self, sourcePath, outputPath, templatesPath) :
        '''
            Initializes the StaticGenerator object with the absolute path to the
            website source folder, and output directory.
        '''
        log.debug("StaticGenerator.__init__(3) with sourcePath="+sourcePath+", outputPath="+outputPath+", templatesPath="+templatesPath)

        self.sourcePath = sourcePath
        self.outputPath = outputPath
        self.templatesPath = templatesPath

        self.BuildTree(sourcePath)
        self.InitMeta()
        self.InitSections()


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializers
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def BuildTree(self,filePath) :
        '''Build the directory tree recursively from 'filePath'.'''
        log.debug("StaticGenerator.BuildTree(1) with filePath="+filePath)

        contentList = os.listdir(filePath)
        fileList = []
        for content in contentList :
            path = os.path.join(filePath,content)
            if os.path.isdir(path) :
                self.BuildTree(path)
            else :
                fileList.append(content)
        self.tree[filePath[len(self.sourcePath):]+"/"]=fileList

    def InitMeta(self) :
        ''' Initialize the meta content from $sourcePath/meta-content.txt.'''
        log.debug("StaticGenerator.InitMeta()")

        metaFilePath = self.sourcePath+"meta-content.txt"
        try:
            content, name =self.ReadYaml(metaFilePath)
        except yaml.YAMLError, exc:
            raise 
        self.meta = content

    def InitSections(self) :
        ''' Initialize the section list, and checks that it matches the content of page_order.'''
        log.debug("StaticGenerator.InitSections()")

        # Sections are defined by the meta-content
        self.sections = self.meta["page_order"]
        # Log mismatch between directories and page_order
        directorySections = list()
        for directory in self.tree :
            strippedName = directory.rstrip("/").decode(encoding='UTF-8')
            if strippedName != "":
                directorySections.append(strippedName)
        for directory in directorySections :
            if self.sections.count(directory) == 0 :
                log.warning("The directory "+directory+" exists within the source directory "+ 
                            self.sourcePath+" but does not appear in the page_order field of "+
                            self.sourcePath+"meta-content.txt.")
        for section in self.sections :
            if directorySections.count(section) == 0 :
                log.warning("The section '"+section+"' appears in the page_order field of "+
                            self.sourcePath+"meta-content.txt but does not correspond "+
                            "to a directory of "+self.sourcePath+".")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Utilities
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ReadYaml(self,filePath) :
        '''
            Read a file that (should) contain YAML and return its content (as a 
            dictionary), and its contentType (name without the extension).
        '''
        log.debug("StaticGenerator.ReadYaml(1) with filePath="+filePath)

        directory, fileName = os.path.split(filePath)
        contentType, extension = os.path.splitext(fileName)
        try :
            content = yaml.load(open(filePath,"r").read())
            log.info( "Parsed "+filePath+". Contains valid YAML of type "+str(contentType))
        except yaml.YAMLError, exc:
            log.error(filePath+" contains invalid YAML. [Error on line "+
                      str(exc.problem_mark.line+1)+", column "+str(exc.problem_mark.column+1)+"].")
            raise 
        return content, contentType

    def GetTemplate(self,templateName) :
        '''Fetch a template from a path relative to the generator.'''
        log.debug("StaticGenerator.GetTemplate(1) with templateName="+templateName)

        templateLoader = jinja2.FileSystemLoader(searchpath = self.templatesPath) 
        env = jinja2.Environment( loader = templateLoader )
        return env.get_template( templateName )


    def RenderTemplate(self,pageTemplate,substitutions,url) :
        '''
            Render a HTML page using a substitution dictionary and a template. 
            Save the output to the output path.
        '''
        log.debug("StaticGenerator.RenderTemplate(3) with pageTemplate="+pageTemplate.name+", substitutions=[see next line], url="+url)
        log.debug(pp.pformat(substitutions))

        # Generate html page
        f = open(self.outputPath + url,"w")
        f.write(pageTemplate.render(dict(substitutions.items()+self.meta.items())).encode('utf8'))
        f.close()


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Generators
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GenerateWebsite(self) :
        '''Trigger complete website generation.'''
        log.debug("StaticGenerator.GenerateWebsite(0)")

        for directory in self.tree :
            for f in self.tree[directory]:
                path=self.sourcePath+directory+f
                if Helper().isYaml(path) :
                    content, contentType = self.ReadYaml(path)
                    if (contentType=="picture-content") :
                        self.GeneratePicturePage(directory.rstrip("/"),content)
                    if (contentType=="text-content") :
                        self.GenerateTextPage(directory.rstrip("/"),content)

    def GenerateHeaderNav(self,name) :
        '''
            Generate header navigation links. Return each link as HTML code, in a list.
            Accounts for the calling location through 'name': this page will be defined
            as 'active' in the header navigation links. 
        '''
        log.debug("StaticGenerator.GenerateHeaderNav(1) with name="+name)

        headerNavTemplate = self.GetTemplate("nav-header-element.tpl")
        substitutions = list()
        for section in self.sections :
            templateVariables = dict()
            if section == name.decode(encoding='UTF-8') :
                templateVariables["active"] = True
            templateVariables["page_url"] = Helper().URLFromDirectory(section,self.meta["landing_page"])
            templateVariables["page_name"] = section
            substitutions.append(headerNavTemplate.render(templateVariables))
        return substitutions

    def GeneratePicturePage(self,directory,contentDictionary) :
        '''
            Generate a picture page (HTML render included).
        '''
        log.debug("StaticGenerator.GeneratePicturePage(2) with directory="+directory+", contentDictionary=")
        log.debug(pp.pformat(contentDictionary))

        
        # fetch templates
        pageTemplate = self.GetTemplate("picture-page.tpl")
        navContentElementTemplate = self.GetTemplate("nav-content-element.tpl")
        pictureElementTemplate = self.GetTemplate("picture-element.tpl")
        substitutions = {"headerNav":[],"contentNav":[],"yearNav":[],"workList":[]}

        # Generate base navigation
        substitutions["headerNav"] = self.GenerateHeaderNav(directory)

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
        self.RenderTemplate(pageTemplate,substitutions,Helper().URLFromDirectory(directory,self.meta["landing_page"]))


    def GenerateTextPage(self,directory,contentDictionary) :
        '''
            Generate a text page (HTML render included).
        '''
        log.debug("StaticGenerator.GenerateTextPage(2) with directory="+directory+", contentDictionary=")
        log.debug(pp.pformat(contentDictionary))

        # fetch templates
        pageTemplate = self.GetTemplate("text-page.tpl")
        textImageTemplate = self.GetTemplate("text-image.tpl")
        textContentTemplate = self.GetTemplate("text-content.tpl")

        # Generate base navigation
        substitutions=dict()
        substitutions["headerNav"] = self.GenerateHeaderNav(directory)
        
        # Check for special page token (currently supported: CONTACT_FORM)
        if contentDictionary["header"] == "CONTACT_FORM" :
            formContactTemplate = self.GetTemplate("form-contact.tpl")
            substitutions["content_text"]=formContactTemplate.render()
        # Default case
        else : 
            # Fetch text page image
            substitutions["content_image"] =  textImageTemplate.render({"image_url":contentDictionary["image"]})

            # Fetch text: render header, then content.
            text = textContentTemplate.render({"text_content":contentDictionary["header"].split("\n")}) 
            for section in contentDictionary["sections"] :
                templateVariables = {"text_section_title":section["name"], "text_content": section["content"].split("\n") }
                text = text+textContentTemplate.render(templateVariables)
            substitutions["content_text"] = text

        self.RenderTemplate(pageTemplate,substitutions,Helper().URLFromDirectory(directory,self.meta["landing_page"]))


class FileManager:
    '''Manage the file system for StaticGenerator.'''

    def __init__(self, sourceBasePath, templateBasePath, temporaryBasePath, outputBasePath) :
        self.sourceBasePath = sourceBasePath
        self.templateBasePath = templateBasePath
        self.temporaryBasePath = temporaryBasePath
        self.outputBasePath = outputBasePath


    def GetUniqueName(self, uniqueString) :
        m=hashlib.sha1()
        m.update(uniqueString)
        return m.hexdigest()

    def Encode(self, fileName) :
        uniqueTemporaryName = self.GetUniqueName(fileName)
        os.system("iconv -f $(file --mime-encoding "+fileName+" | awk '{ print $2 }') -t utf-8 "+fileName+" > "+uniqueTemporaryName)
        os.system("mv "+uniqueTemporaryName+" "+fileName)
        os.system("rm "+uniqueTemporaryName)

    def ResizeForThumbnails(self,originalPath,finalPath) :
        os.system("convert -resize 250x "+originalPath+" "+finalPath)

    def ResizeForWeb(self,originalPath,finalPath) :
        os.system("convert -resize x750 "+originalPath+" "+finalPath)
        

    def CleanOutputDirectory(self) :
        logging.info("Removing tree "+self.statGen.outputPath)
        shutil.rmtree(self.statGen.outputPath,ignore_errors=True)

    def SetupOutputDirectory(self) :
        logging.info("Copying js to "+self.statGen.outputPath+"js")
        shutil.copytree("js",self.statGen.outputPath+"js")
        logging.info("Copying css to "+self.statGen.outputPath+"css")
        shutil.copytree("css",self.statGen.outputPath+"css")
        logging.info("Copying img to "+self.statGen.outputPath+"img")
        shutil.copytree("img",self.statGen.outputPath+"img")
        logging.info("Creating "+self.statGen.outputPath+"img/work/")
        try : os.mkdir(self.statGen.outputPath+"img/work/")
        except OSError: pass
        logging.info("Creating "+self.statGen.outputPath+"img/thumb/")
        try : os.mkdir(self.statGen.outputPath+"img/thumb/")
        except OSError: pass

    # def SourceValidate(self) :
        # Validate the source directory sanity (UTF 8, depth)
    
        # # Move files
        # for element in contentDictionary["Files"] :
        #     shutil.copyfile(self.sourcePath+name+"/"+element["path"],self.outputPath+"img/work/"+element["path"])
        #     shutil.copyfile(self.sourcePath+name+"/"+element["path"],self.outputPath+"img/thumb/"+element["path"])