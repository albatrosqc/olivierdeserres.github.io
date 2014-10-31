#!/usr/bin/python
import time, datetime, sys, logging, pprint
import yaml
from staticgenerator import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


# Dependencies of the project
#  OS/binaries:
#   - Linux is recommended
#   - imagemagick suite (convert for thumbnails / websized images, identify to fetch info)
#   - file (to extract charset mimetype)
#   - iconv (conversion between charsets)
# 
#  Python:
#   - PyYaml
#   - watchdog
#   - jinja2


def Now() :
    return datetime.datetime.now().strftime("[%d-%m-%Y %H:%M] ")

class EventHandler(FileSystemEventHandler) :

    def __init__(self, observer, conf) :
        self.observer = observer
        self.conf = conf
        
    def on_any_event(self, event) :
        # Log event
        eventKey = event.key
        print Now()+eventKey[0]+" "+eventKey[1]+" (is_directory == "+str(eventKey[2])+")"
        # Try to generate the page
        try :
            print Now()+"Initialization of StaticGenerator."
            sg = StaticGenerator(self.conf["source_path"],self.conf["target_path"],self.conf["templates_path"])
            print Now()+"Generating website."
            sg.GenerateWebsite()
        except IOError as exc:
            print Now()+str(exc)
        except yaml.YAMLError as exc:
            print Now()+str(exc)
        except :
            print Now()+"Unexpected error:", sys.exc_info()[0]
            pass

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