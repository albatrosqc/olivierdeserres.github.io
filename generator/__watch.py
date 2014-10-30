import time
import sys
import logging
import shutil
from pprint import pformat
from staticgenerator import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class StatGenEvenHandler(FileSystemEventHandler) :
    def __init__(self, observer, statGen) :
        self.observer = observer
        self.statGen = statGen
        logging.basicConfig(filename='generator.log',level=logging.INFO, format='[%(levelname)s] %(asctime)s : %(message)s', datefmt='%d-%m-%y %H:%M:%S')
        
    def on_any_event(self, event) :
        eventKey = event.key
        logging.info(eventKey[0]+" "+eventKey[1]+" (is_directory == "+str(eventKey[2])+")")
        logging.info("CleanOutputDirectory()")
        self.CleanOutputDirectory()
        logging.info("SetupOutputDirectory()")
        self.SetupOutputDirectory()
        logging.info("GenerateWebsite()")
        success = self.statGen.GenerateWebsite()
        logging.info("Operation successful.")

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






def main(argv=None):
    dropboxPath="/root/Dropbox/olivierdeserres/"
    target="/root/olivierdeserres.github.io/generated/"

    sg = StaticGenerator(dropboxPath,target)

    observer = Observer()
    event_handler = StatGenEvenHandler(observer,sg)

    observer.schedule(event_handler, dropboxPath, recursive=True)
    observer.start()
    try: 
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))