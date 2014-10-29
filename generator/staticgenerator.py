#!/usr/bin/python

from jinja2 import Environment, FileSystemLoader
import os
import yaml

class StaticGenerator :
    """
        Generate html content from a Dropbox folder.
    """

    # Data members
    tree=dict()
    dropboxPath=""

    def __init__(self, dropboxPath) :
        """
            Constructor: initialize with the absolute path to the DropBox folder.
        """
        self.dropboxPath = dropboxPath

    def BuildTree(self,currentPath) :
        """ 
            Recursive directory tree builder.
        """

        contentList = os.listdir(currentPath)
        fileList = []

        for content in contentList :
            path = os.path.join(currentPath,content)
            if os.path.isdir(path) :
                self.BuildTree(path)
            else :
                fileList.append(content)

        self.tree[currentPath[len(self.dropboxPath):]+"/"]=fileList

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

        return name, {"Files":None} 

    def ScanDirectory(self) :
        self.BuildTree(self.dropboxPath)
        for directory in self.tree :
            for f in self.tree[directory]:
                path=self.dropboxPath+directory+f
                return name, content = self.ReadFile(path)

