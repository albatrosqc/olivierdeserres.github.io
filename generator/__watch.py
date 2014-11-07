#!/usr/bin/python
import time
import datetime
import sys
import logging
import pprint
import threading
import yaml
import traceback
from staticgenerator import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def Now():
    return datetime.datetime.now().strftime("[%d-%m-%Y %H:%M:%S] ")


class EventHandler(FileSystemEventHandler):
    def __init__(self, observer, conf):
        self.observer = observer
        self.conf = conf
        self.timerActive = False

    def on_any_event(self, event):
        # Log event
        eventKey = event.key
        print(Now(), eventKey[0], " ", eventKey[1],
              " (is_directory == ", eventKey[2], ")")

        # Init countdown to update
        if self.timerActive:
            self.delayedFunction.cancel()
        self.timerActive = True
        self.delayedFunction = threading.Timer(self.conf["update_delay"],
                                               self.generate_action)
        self.delayedFunction.start()
      
    def generate_action(self):
        self.timerActive = False
        self.delayedFunction.cancel()
        # Try to generate the page
        fm = FileManager(self.conf)
        try:
            print(Now(), "Probing paths...")
            fm.Probe()

            print(Now(), "Updating resource list...")
            fm.UpdateResourceList()

            print(Now(), "Preparing temporary directory...")
            fm.SetupTemporaryDirectory()

            print(Now(), "Modifying file names using a unified naming scheme.")
            fm.PrettifyFileNames()

            # print(Now(), "Converting images...")
            # fm.ProcessImages()

            print(Now(), "Initialization of StaticGenerator.")
            sg = StaticGenerator(self.conf["source_path"],
                                 self.conf["temporary_path"],
                                 self.conf["templates_path"])
            print(Now(), "Generating website.")
            sg.GenerateWebsite()
            print(Now(), "All done!")

        except MissingCrucial as exc:
            print(Now(), str(exc))
            print(Now(), "Won't generate.")
            pass
        except ProbingErrorRestart:
            print(Now(), "Temporary output directory already exists.")
            try:
                fm.DeleteDir(self.conf["temporary_path"])
                self.generate_action()
            except OSError as exc:
                print(Now(),
                      "Tried to remove the temporary directory but got:",
                      exc.strerror)
                print(Now(), "Won't generate.")
                pass
        except ProbingError as exc:
            print(Now(), str(exc))
            print(Now(), "Won't generate.")
            pass
        except:
                excInfo=sys.exc_info()
                print(Now(), "Unexpected error of type:", excInfo[0])
                print(Now(), "Reason:", excInfo[1])
                traceback.print_tb(excInfo[2])

def main(argv=None):

    conf = yaml.load(open("configuration.yml","r").read())
    print(Now(), "Configuration file loaded with success.")
    pprint.pprint(conf)

    obs = Observer()
    event_handler = EventHandler(obs,conf)
    obs.schedule(event_handler, conf["source_path"], recursive=True)
    obs.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
        return 1

    obs.stop()
    obs.join()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))