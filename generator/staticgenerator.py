#!/usr/bin/python

from jinja2 import Environment, FileSystemLoader
import os
import shutil

class StaticGenerator :
    def __init__(self, dropboxPath):
        """
            Constructor: initialize with the absolute path to the DropBox folder.
        """
        self.dropboxPath = dropboxPath

    def directoryScanner

        baseDirectoryContent = os.listdir(self.dropboxPath)

        for dirName in baseDirectoryContent :
            self.tree[dirName] = os.listdir(self.dropboxPath+dirName)

