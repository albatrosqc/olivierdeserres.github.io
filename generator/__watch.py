#!/usr/bin/python
import time, datetime, sys, logging, pprint, threading
import yaml
from staticgenerator import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

def Now() :
    return datetime.datetime.now().strftime("[%d-%m-%Y %H:%M:%S] ")

class EventHandler(FileSystemEventHandler) :

    def __init__(self, observer, conf) :
        self.observer = observer
        self.conf = conf
        self.timerActive = False

    def on_any_event(self, event) :
        # Log event
        eventKey = event.key
        print Now()+eventKey[0]+" "+eventKey[1]+" (is_directory == "+str(eventKey[2])+")"

        # Init countdown to update
        if self.timerActive :
            self.delayedFunction.cancel()
        self.timerActive = True
        self.delayedFunction = threading.Timer(self.conf["update_delay"], self.generate_action)
        self.delayedFunction.start()
      

    def generate_action(self) :
        self.timerActive = False
        self.delayedFunction.cancel()
        # Try to generate the page
        fm = FileManager(self.conf)
        try :

            print Now()+"Probing paths..."
            fm.Probe()

            print Now()+"Updating resource list..."
            fm.UpdateResourceList()

            print Now()+"Preparing temporary directory..."
            fm.SetupTemporaryDirectory()

            print Now()+"Modifying file names using a unified naming scheme..."
            fm.PrettifyFileNames()

            print Now()+"Converting images..."
            fm.ProcessImages()

            try :
                print Now()+"Initialization of StaticGenerator."
                sg = StaticGenerator(self.conf["source_path"],self.conf["temporary_path"],self.conf["templates_path"])
                print Now()+"Generating website."
                sg.GenerateWebsite()
            except IOError as exc:
                print Now()+str(exc)
                raise
            except yaml.YAMLError as exc:
                print Now()+str(exc)
                raise
            except :
                print Now()+"Unexpected error in StaticGenerator:", sys.exc_info()[0]

            print Now()+"All done!"

        except Exception as exc :
            if str(exc)=="Temporary output directory already exists." :
                print Now()+str(exc)+"["+self.conf["temporary_path"]+"]"
                try :
                    fm.DeleteDir(self.conf["temporary_path"])
                    self.generate_action()
                except  OSError as exc:
                    print Now()+"Tried to remove the temporary directory but got :" + exc.strerror
                    print Now()+"Won't generate."
            elif str(exc)=="Template directory does not exists." :
                print Now()+str(exc)+"["+self.conf["templates_path"]+"]"
                print Now()+"Won't generate."
            elif str(exc)=="Output directory does not exists." :
                print Now()+str(exc)+"["+self.conf["target_path"]+"]"
                fm.MakeDir(self.conf["target_path"])
                self.generate_action()
            elif str(exc)=="Missing meta-content.txt":
                print Now()+str(exc)
            else :
                print Now()+"Unexpected error:", sys.exc_info()[0]

def main(argv=None):

    conf = yaml.load(open("configuration.yml","r").read())
    print Now()+"Configuration file loaded with success."
    pprint.pprint(conf)

    obs = Observer()
    event_handler = EventHandler(obs,conf)
    obs.schedule(event_handler, conf["source_path"], recursive=True)
    obs.start()

    try :
        while True :
            time.sleep(1)
    except KeyboardInterrupt :
        obs.stop()
        return 1

    obs.stop()
    obs.join()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))