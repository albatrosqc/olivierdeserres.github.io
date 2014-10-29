from staticgenerator import *
from pprint import PrettyPrinter 

# Redacted for privacy
dbpath="~/Dropbox/olivierdeserres/"
outpath="~/olivierdeserres.github.io/test/"
pp = PrettyPrinter(indent=2) 
sg = StaticGenerator(dbpath,outpath,"travaux")

print "================================="
print "Dropbox tree:\n"
pp.pprint(sg.tree)
print "\n"

print "================================="
print "Meta information:\n"
pp.pprint(sg.meta)
print "\n"

sg.GenerateWebsite()