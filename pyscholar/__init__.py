import os, ConfigParser
#Check if .pyscholar exists and create it if necessary
pyscholarDir = os.path.join(os.path.expanduser("~"), ".pyscholar")
if not os.path.exists(pyscholarDir):
    os.makedirs(pyscholarDir)

#Same for .pyscholar/keys.cfg
if not os.path.exists(os.path.join(pyscholarDir, "keys.cfg")):
    keysParser = ConfigParser.ConfigParser()
    keysParser.add_section("Keys")
    keysParser.set('Keys', 'Scopus', "")
    originalMask = os.umask(0)
    keysDescriptor = os.open(os.path.join(pyscholarDir, 'keys.cfg'), os.O_WRONLY | os.O_CREAT, 0666)
    keysFile = os.fdopen(keysDescriptor, 'w')
    os.umask(originalMask)
    keysParser.write(keysFile)
    keysFile.close()

import scopus
import network
import layout
