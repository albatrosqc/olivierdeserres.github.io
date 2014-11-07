#!/usr/bin/python
import jinja2
import yaml
from PIL import Image
import hashlib
import os
import shutil
import logging
import pprint as pp

# Configure logger
logging.basicConfig(filename='generator.log', level=logging.DEBUG,
                    format='[%(levelname)s] %(asctime)s : %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S')
log = logging.getLogger("staticgenerator")

# Exceptions
class ProbingError(Exception):
    ''' Fatal probing error that should stop the process. '''
    pass


class ProbingErrorRestart(Exception):
    ''' Fatal probing error that should stop the process. '''
    pass


class MissingCrucial(Exception):
    ''' Missing crucial element (e.g. YAML file). '''
    pass


class Helper:
    '''
        Small helper function that are useful for both
        StaticGenerator and FileManager.
    '''

    # Data members
    tree = dict()

    def __init__(self):
        ''' Empty constructor; useful for direct usage within other classes'''
        log.debug("Helper.__init__[0]")

    def BuildTree(self, filePath, absoluteBase):
        '''Build the directory tree recursively from 'filePath'.'''
        log.debug("Helper.BuildTree[1] with filePath=" + filePath)

        contentList = os.listdir(filePath,)
        fileList = []
        for content in contentList:
            path = os.path.join(filePath, content)
            if os.path.isdir(path):
                self.BuildTree(path, absoluteBase)
            else:
                fileList.append(content)
        self.tree[filePath[len(absoluteBase):] + "/"] = fileList
        return self.tree

    def isYaml(self,filePath):
        '''
            Override the default exception behavior of yaml.load(1) to turn
            it into a simple test of validity.
        '''
        log.debug("Helper.isYaml[1] with filePath=" + filePath)

        try:
            yaml.load(open(filePath, "r").read())
            return True
        except:
            return False

    def ReadYaml(self, filePath):
        '''
            Read a file that (should) contain YAML and return its content
            (as a dictionary), and its contentType (name without the
            extension).
        '''
        log.debug("Helper.ReadYaml[1] with filePath=" + filePath)

        directory, fileName = os.path.split(filePath)
        contentType, extension = os.path.splitext(fileName)
        try:
            content = yaml.load(open(filePath, "r").read())
            log.info("Parsed " + filePath +
                     ". Contains valid YAML of type " + str(contentType))
        except yaml.YAMLError as exc:
            log.error(filePath + " contains invalid YAML. [Error on line " +
                      str(exc.problem_mark.line + 1) +
                      ", column " + str(exc.problem_mark.column + 1) + "].")
            raise
        return content, contentType

    def URLFromDirectory(self, directory, index=""):
        '''
            Define a unique correspondence between a directory name
            and a URL. Unified use of this functions enforce a unified
            naming scheme.
            A directory that holds the content of the index is associated to
            'index.html' automatically.
        '''
        log.debug("Helper.URLFromDirectory[2] with directory=" +
                  directory + ", index=" + index)

        if (directory == index):
            return "index.html"
        else:
            return directory.rsplit(" ")[-1] + ".html"

    def PrettifiedFileName(self, filename):
        '''
            Define a unique correspondence between a file name
            and a prettified file name (lowercase, underscore for whitespace).
            Unified use of this functions enforce a unified naming scheme.
        '''
        log.debug("Helper.PrettifiedFileName[1] with filename=" + filename)

        return filename.lower().replace(" ", "_")

    def GetTemplate(self, templateName, templatePath):
        '''Fetch a template from a path relative to the generator.'''
        log.debug("Helper.GetTemplate[2] with templateName=" +
                  templateName + ", templatesPath=" + templatePath)

        templateLoader = jinja2.FileSystemLoader(searchpath=templatePath)
        env = jinja2.Environment(loader=templateLoader)
        return env.get_template(templateName)


class StaticGenerator:
    '''
        Generate HTML content from a source folder that follows the
        appropriate pattern.
    '''

    # Data members
    tree = dict()
    meta = dict()
    sections = list()
    sourcePath = ""
    outputPath = ""
    templatesPath = ""

    def __init__(self, sourcePath, outputPath, templatesPath):
        '''
            Initializes the StaticGenerator object with the absolute path to
            the website source folder, and output directory.
        '''
        log.debug("StaticGenerator.__init__[3] with sourcePath=" +
                  sourcePath + ", outputPath=" + outputPath +
                  ", templatesPath=" + templatesPath)

        self.sourcePath = sourcePath
        self.outputPath = outputPath
        self.templatesPath = templatesPath

        self.tree = Helper().BuildTree(sourcePath, sourcePath)
        self.InitMeta()
        self.InitSections()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializers
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def InitMeta(self):
        ''' Initialize the meta content from $sourcePath/meta-content.txt.'''
        log.debug("StaticGenerator.InitMeta()")

        metaFilePath = self.sourcePath + "meta-content.txt"
        try:
            content, name = Helper().ReadYaml(metaFilePath)
        except yaml.YAMLError:
            raise
        self.meta = content

    def InitSections(self):
        '''
            Initialize the section list, and checks that it matches the
            content of page_order.
        '''
        log.debug("StaticGenerator.InitSections()")

        # Sections are defined by the meta-content
        self.sections = self.meta["page_order"]
        # Log mismatch between directories and page_order
        directorySections = list()
        for directory in self.tree:
            strippedName = directory.rstrip("/") 
            if strippedName != "":
                directorySections.append(strippedName)
        for directory in directorySections:
            if self.sections.count(directory) == 0:
                log.warning("The directory " + directory + " exists within " +
                            "the source directory " + self.sourcePath + " " +
                            "but does not appear in the page_order " +
                            "field of " + self.sourcePath +
                            "meta-content.txt.")
        for section in self.sections:
            if directorySections.count(section) == 0:
                log.warning("The section '" + section + "' appears in the " +
                            "page_order field of " + self.sourcePath +
                            "meta-content.txt but does not correspond " +
                            "to a directory of " + self.sourcePath + ".")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Utilities
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RenderTemplate(self, pageTemplate, substitutions, url):
        '''
            Render a HTML page using a substitution dictionary and a template.
            Save the output to the output path.
        '''
        log.debug("StaticGenerator.RenderTemplate[3] with pageTemplate=" +
                  pageTemplate.name + ", substitutions=[see next line], url=" +
                  url)
        log.debug(pp.pformat(substitutions))

        # Generate html page
        f = open(self.outputPath + url, "w")
        f.write(pageTemplate.render(dict(substitutions.items() +
                self.meta.items())))
        f.close()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Generators
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GenerateWebsite(self):
        '''Trigger complete website generation.'''
        log.debug("StaticGenerator.GenerateWebsite[0]")

        for directory in self.tree:
            for f in self.tree[directory]:
                path = self.sourcePath + directory + f
                print(path)
                if Helper().isYaml(path):
                    content, contentType = Helper().ReadYaml(path)
                    if (contentType == "picture-content"):
                        self.GeneratePicturePage(directory.rstrip("/"),
                                                 content)
                    if (contentType == "text-content"):
                        self.GenerateTextPage(directory.rstrip("/"),
                                              content)

    def GenerateHeaderNav(self, name):
        '''
            Generate header navigation links. Return each link as HTML code,
            in a list.
            Accounts for the calling location through 'name': this page will
            be defined as 'active' in the header navigation links.
        '''
        log.debug("StaticGenerator.GenerateHeaderNav[1] with name=" + name)

        headerNavTemplate = Helper().GetTemplate("nav-header-element.tpl",
                                                 self.templatesPath)
        substitutions = list()
        for section in self.sections:
            templateVariables = dict()
            if section == name:
                templateVariables["active"] = True
            templateVariables["page_url"] =\
                Helper().URLFromDirectory(section, self.meta["landing_page"])
            templateVariables["page_name"] = section
            substitutions.append(headerNavTemplate.render(templateVariables))
        return substitutions

    def GeneratePicturePage(self, directory, contentDictionary):
        '''
            Generate a picture page (HTML render included).
        '''
        log.debug("StaticGenerator.GeneratePicturePage[2] with directory=" +
                  directory + ", contentDictionary=")
        log.debug(pp.pformat(contentDictionary))

        # fetch templates
        pageTemplate = Helper().GetTemplate("picture-page.tpl",
                                            self.templatesPath)
        navContentElementTemplate =\
            Helper().GetTemplate("nav-content-element.tpl", self.templatesPath)
        pictureElementTemplate =\
            Helper().GetTemplate("picture-element.tpl", self.templatesPath)
        substitutions = {"headerNav": [], "contentNav": [],
                         "yearNav": [], "workList": []}

        # Generate base navigation
        substitutions["headerNav"] = self.GenerateHeaderNav(directory)

        # Determine extra navigations
        uniqueCategories = list()
        uniqueYears = list()
        for element in contentDictionary["Files"]:
            if uniqueCategories.count(element["category"]) == 0:
                uniqueCategories.append(element["category"])
            if uniqueYears.count(element["year"]) == 0:
                uniqueYears.append(element["year"])
        # Generate extra navigations
        substitutions["allNav"] =\
            navContentElementTemplate.render({"category_url": "",
                                             "category_name": "toutes"})
        for element in uniqueCategories:
            templateVariables = {"category_url": element,
                                 "category_name": element}
            substitutions["contentNav"].append(
                navContentElementTemplate.render(templateVariables))
        for element in uniqueYears:
            templateVariables = {"category_url": element,
                                 "category_name": element}
            substitutions["yearNav"].append(
                navContentElementTemplate.render(templateVariables))

        # Generate workList
        for element in contentDictionary["Files"]:
            templateVariables =\
                {"category_name": element["category"],
                 "image_title": element["title"],
                 "image_spec": element["spec"],
                 "image_url": "img/work/" +
                    Helper().PrettifiedFileName(element["path"]),
                 "image_thumbnail_url": "img/thumb/" +
                    Helper().PrettifiedFileName(element["path"]),
                 "image_year": element["year"]}
            substitutions["workList"].append(
                pictureElementTemplate.render(templateVariables))

        # Generate html page
        self.RenderTemplate(pageTemplate, substitutions,
                            Helper().URLFromDirectory(
                                directory, self.meta["landing_page"]))

    def GenerateTextPage(self, directory, contentDictionary):
        '''
            Generate a text page (HTML render included).
        '''
        log.debug("StaticGenerator.GenerateTextPage[2] with directory=" + directory + ", contentDictionary=")
        log.debug(pp.pformat(contentDictionary))

        # fetch templates
        pageTemplate = Helper().GetTemplate("text-page.tpl",
                                            self.templatesPath)
        textImageTemplate = Helper().GetTemplate("text-image.tpl",
                                                 self.templatesPath)
        textContentTemplate = Helper().GetTemplate("text-content.tpl",
                                                   self.templatesPath)

        # Generate base navigation
        substitutions=dict()
        substitutions["headerNav"] = self.GenerateHeaderNav(directory)

        # Check for special page token (currently supported: CONTACT_FORM)
        if contentDictionary["header"] == "CONTACT_FORM":
            formContactTemplate = Helper().GetTemplate("form-contact.tpl", self.templatesPath)
            substitutions["content_text"]=formContactTemplate.render()
        # Default case
        else: 
            # Fetch text page image
            substitutions["content_image"] =  textImageTemplate.render({"image_url":contentDictionary["image"]})

            # Fetch text: render header, then content.
            text = textContentTemplate.render({"text_content":contentDictionary["header"].split("\n")}) 
            for section in contentDictionary["sections"]:
                templateVariables = {"text_section_title":section["name"], "text_content": section["content"].split("\n") }
                text = text+textContentTemplate.render(templateVariables)
            substitutions["content_text"] = text

        self.RenderTemplate(pageTemplate,substitutions,Helper().URLFromDirectory(directory,self.meta["landing_page"]))


class FileManager:
    '''Manage the file system for StaticGenerator.'''

    resourceTree=dict()

    def __init__(self, config):
        self.sourceBasePath = config["source_path"]
        self.templateBasePath = config["templates_path"]
        self.temporaryBasePath = config["temporary_path"]
        self.targetPath = config["target_path"]
        self.forceRemove = config["force_remove"]
        self.imageFileExtensions = config["image_file_extensions"]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Utilities
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def GetUniqueName(self, uniqueString):
        m=hashlib.sha1()
        m.update(uniqueString)
        return m.hexdigest()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Image related
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ProcessImages(self):
        '''
            Process images from the source directory and place the resulting images 
            in the temporary directory.
        '''
        log.debug("FileManager.ProcessImages[0]")
        
        for directory in self.resourceTree:
            if self.resourceTree[directory].count("picture-content.txt")>0:
                for image in self.resourceTree[directory]:
                        if self.imageFileExtensions.count(os.path.splitext(image)[1]) > 0:
                            prettyImageName = Helper().PrettifiedFileName(image)
                            log.info("Processing "+self.sourceBasePath+directory+prettyImageName)
                            self.CreateThumbnail(self.temporaryBasePath+"tmp_images/"+prettyImageName,self.temporaryBasePath+"img/thumb/"+prettyImageName)
                            self.ResizeForWeb(self.temporaryBasePath+"tmp_images/"+prettyImageName,self.temporaryBasePath+"img/work/"+prettyImageName)

        shutil.rmtree(self.temporaryBasePath+"tmp_images/",ignore_errors=True)

    def CreateThumbnail(self,originalPath,targetPath):
        '''
        '''
        log.debug("FileManager.CreateThumbnail[2] with originalPath="+originalPath+", targetPath="+targetPath)

        im = Image.open(originalPath)
        width, height = im.size
        output = im.resize( (250, int(height*250/width)), Image.ANTIALIAS)
        output.save(targetPath)

    def ResizeForWeb(self,originalPath,targetPath):
        '''
        '''
        log.debug("FileManager.ResizeForWeb[2] with originalPath="+originalPath+", targetPath="+targetPath)

        im = Image.open(originalPath)
        width, height = im.size
        output = im.resize( (int(width*750/height), 750), Image.ANTIALIAS)
        output.save(targetPath)



    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Files related
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateResourceList(self):
        '''
            Update directory tree and prepare directories / move files.
        '''
        log.debug("FileManager.UpdateResourceList[0]")
        self.resourceTree = Helper().BuildTree(self.sourceBasePath,self.sourceBasePath)

    def SetupTemporaryDirectory(self):
        '''
            Create subdirectories and move constant files to the temporary directory.
        '''
        log.debug("FileManager.SetupTemporaryDirectory[0]")

        # Copy basic apps/css/img
        shutil.copytree(self.templateBasePath+"js",self.temporaryBasePath+"js")
        shutil.copytree(self.templateBasePath+"css",self.temporaryBasePath+"css")
        shutil.copytree(self.templateBasePath+"img",self.temporaryBasePath+"img")

        # Setup tmp image directory
        self.MakeDir(self.temporaryBasePath+"tmp_images/")
        
        # Sanity check
        if self.resourceTree.get("/").count("meta-content.txt") == 0:
            raise Exception("Missing meta-content.txt")

        # Copy custom share / background image
        metaContent = Helper().ReadYaml(self.sourceBasePath+"meta-content.txt")
        share_image = metaContent[0]["share_image"]
        background_image = metaContent[0]["background_image"]
        shutil.copy(self.sourceBasePath+share_image, self.temporaryBasePath+"img/"+Helper().PrettifiedFileName(share_image))
        shutil.copy(self.sourceBasePath+background_image, self.temporaryBasePath+"img/"+Helper().PrettifiedFileName(background_image))

        try:
            globalCssTemplate =  Helper().GetTemplate("global.tpl",self.templateBasePath)
            f = open(self.temporaryBasePath+"css/global.css","w")
            backgroundPath = Helper().ReadYaml(self.sourceBasePath+"meta-content.txt")[0]["background_image"]
            f.write(globalCssTemplate.render({"background_image":Helper().PrettifiedFileName(backgroundPath)}))
            f.close()
        except:
            raise Exception("Encountered error while templating global.css.")
        

    def PrettifyFileNames(self):
        '''
            Remove funky character from file names.
        '''
        log.debug("FileManager.PrettifyFileNames[0]")

        for directory in self.resourceTree:
            if self.resourceTree[directory].count("picture-content.txt")>0:
                for image in self.resourceTree[directory]:
                        if self.imageFileExtensions.count(os.path.splitext(image)[1]) > 0:
                            shutil.copy(self.sourceBasePath+directory+image, self.temporaryBasePath+"tmp_images/"+image)
                            shutil.move(self.temporaryBasePath+"tmp_images/"+image, self.temporaryBasePath+"tmp_images/"+Helper().PrettifiedFileName(image))
            if self.resourceTree[directory].count("text-content.txt")>0:
                for image in self.resourceTree[directory]:
                        if self.imageFileExtensions.count(os.path.splitext(image)[1]) > 0:
                            shutil.copy(self.sourceBasePath+directory+image, self.temporaryBasePath+"img/"+image)
                            shutil.move(self.temporaryBasePath+"img/"+image, self.temporaryBasePath+"img/"+Helper().PrettifiedFileName(image))

    def Encode(self, fileName):
        uniqueTemporaryName = self.GetUniqueName(fileName)
        os.system("iconv -f $(file --mime-encoding "+fileName+" | awk '{ print $2 }') -t utf-8 "+fileName+" > "+uniqueTemporaryName)
        os.system("mv "+uniqueTemporaryName+" "+fileName)
        os.system("rm "+uniqueTemporaryName)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Directory related
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def Probe(self):
        '''
            Probe all necessary directories.
        '''
        log.debug("FileManager.Probe[0]")
        try:
            self.ProbeOutputDirectory()
            self.ProbeTemporaryDirectory()
            self.ProbeTemplateDirectory()
        except:
            raise 

    def ProbeOutputDirectory(self):
        '''
            Probe the output directory for write access.
        '''
        log.debug("FileManager.ProbeOutputDirectory[0]")

        if os.access(self.targetPath,os.F_OK):
            if not os.access(self.targetPath,os.W_OK):
                raise ProbingError("Output directory is not writeable.")
        else:
            raise ProbingError("Output directory does not exists.")

    def ProbeTemporaryDirectory(self):
        '''
            Probe the temporary output directory for write access/existence.
        '''
        log.debug("FileManager.ProbeTemporaryDirectory[0]")
        if os.access(self.temporaryBasePath,os.F_OK):
            raise ProbingErrorRestart("Temporary directory already exists.")

    def ProbeTemplateDirectory(self):
        '''
            Probe the template directory for read access.
        '''
        log.debug("FileManager.ProbeTemplateDirectory[0]")
        if os.access(self.templateBasePath,os.F_OK):
            if not os.access(self.templateBasePath,os.R_OK):
                raise MissingCrucial("Template directory is not readable.")
        else:
            raise MissingCrucial("Template directory does not exists.")


    def MakeDir(self,path):
        '''
            Make a directory with proper permissions.
        '''
        log.debug("FileManager.MakeDir[1] with path="+path)

        os.mkdir(path,0o755)
        log.info("Created "+path)

    def DeleteDir(self,path):
        '''
            Delete a directory and pass the error.
        '''
        log.debug("FileManager.DeleteDir[1] with path="+path)
        if self.forceRemove:
            shutil.rmtree(path,ignore_errors=True)
        else:
            try:
                os.rmdir(path)
            except:
                raise

    # def SourceValidate(self):
        # Validate the source directory sanity (UTF 8, depth)
    
        # # Move files
        # for element in contentDictionary["Files"]:
        #     shutil.copyfile(self.sourcePath+name+"/"+element["path"],self.outputPath+"img/work/"+element["path"])
        #     shutil.copyfile(self.sourcePath+name+"/"+element["path"],self.outputPath+"img/thumb/"+element["path"])