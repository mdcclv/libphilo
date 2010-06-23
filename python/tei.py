#!/usr/bin/env python
import xml.parsers.expat
import re
import os
import sys
import codecs
import math
from OHCOVector import *

# First we need to get our outputs taking utf8.  Very Important!
sys.stdout = codecs.getwriter("utf-8")(sys.stdout) 
sys.stderr = codecs.getwriter("utf-8")(sys.stderr)

# Initialize our main data structure.
# There really should be a TeiParser class to contain them.
# But global variables are okay for short scripts like this one.

objects = OHCOVector(["doc","div1","div2","div3","para","sent","word"])
mapping = {"TEI":"doc",
       "front":"div",
       "div":"div",
       "div0":"div",
       "div1":"div",
       "div2":"div",
       "div3":"div",
       "p":"para",
       "sp":"para",
       "stage":"para"}

metamap = { "titleStmt/author" : "author",
            "titleStmt/title" : "title",
            "div/head" : "head"}

metahandler = None

parallel = {"line":0,
        "byte":0}

sortkeys = "-k 1,1 -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n"

context = []
blocksize = 2048
index_cutoff = 10
print objects

def context_match(context,pattern):
    nodes = [x for x in pattern.split("/") if x != ""]
    for node in nodes:
        if node in context:
            position = context.index(node)
            context = context[position:]
        else:
            return False
    return True
    
#next, we start to build up the handlers that will accept expat events.
def tagstart(name,attributes): # I should really wrap this in a class to hold state.
    """translates xml tags into OHCOVector push events 
       by looking them up in a mapping"""
    global metahandler
    parallel["byte"] = parser.CurrentByteIndex
    context.append(name)
    for pattern in metamap:
        if context_match(context,pattern):
            metahandler = metamap[pattern]
    if name in mapping:
        type = mapping[name]
        objects.push(type)
        attlist = ""
        for k,v in attributes.iteritems():
            attlist += " %s=\"%s\"" % (k,v) 
        print >> o, type + " " + "<" + name + attlist + "> " + \
              " ".join(map(str,objects.v)) + " " + str(parallel["byte"]) + \
              " " + str(parallel["line"])
        if type == "doc":
            print >> o, "meta %s %s" % ("filename", filename)

    if name == "l":
        if "n" in attributes.keys():
            parallel["line"] = int(attributes["n"])
        else:
            parallel["line"] += 1
        print >> o, "line %d %d" % (parallel["byte"],parallel["line"])


def tagend(name):
    """translates xml end tags into OHCOVector pull events"""
    global metahandler
    parallel["byte"] = parser.CurrentByteIndex
    for pattern in metamap:
        if context_match(context,pattern):
            metahandler = None
    context.pop()
    if name in mapping:
        type = mapping[name]
        #print "found %s, pulling from %s" % (name, type)
        objects.pull(type)
        print >> o, type + " " + "</" + name + ">" + " ".join(map(str,objects.v)) + \
               " " + str(parallel["byte"]) + " " + str(parallel["line"])
    

def tokenizer(text):
    """uses a regex to split text into sentences and words, 
       and pushes each into the OHCOVector.  A more sophisticated implementation 
       would have a buffer, and check for tag-spanning words, or if we're in a 
       metadata tag, and dispatch tokens accordingly."""
    parallel["byte"] = parser.CurrentByteIndex
    tokens = re.finditer(ur"([\w\u2019]+)|([\.;:?!])",text,re.U)
    offset = parallel["byte"]
    if metahandler:
        cleantext = re.sub("[\n\t]"," ",text)
        print >> o, "meta %s %s" % (metahandler,cleantext)
    for token in tokens:
        if token.group(1):
            objects.push("word")
            char_offset = token.start(1)
            byte_length = len(text[:char_offset].encode("UTF-8"))
            print >> o, "word " + token.group(1) + " " + " ".join(map(str,objects.v)) \
                  + " " + str(offset + byte_length) + " " + str(parallel["line"])
        if token.group(2):
            objects.push("sent")
            char_offset = token.start(1)
            byte_length = len(text[:char_offset].encode("UTF-8"))
            print >> o, "sent " + token.group(2) + " " + " ".join(map(str,objects.v)) \
                   + " " + str(offset + byte_length) + " " + str(parallel["line"])
    return 0


def default(data):
    parallel["byte"] = parser.CurrentByteIndex


#the main outer loop.
print "starting up expat"
fileinfo = []
workdir = os.path.commonprefix(sys.argv[1:])
for file in sys.argv[1:]: # not counting argv[0], which is the name of the program.
    offset = 0
    f = open(file)
    filename = os.path.basename(file)
    path = os.path.abspath(file)
    outpath = path + ".raw"
    o = codecs.open(outpath, "w", "utf-8")
    print "parsing %s @ %s" % (filename,path)
    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = tagstart
    parser.EndElementHandler = tagend
    parser.CharacterDataHandler = tokenizer
    parser.ParseFile(f)
    fileinfo.append({"path":path,"name":filename,"raw":outpath})

print "parsed %d files successfully." % len(fileinfo)
for file in fileinfo:
    print "sorting %s" % file["name"]
    file["words"] = file["path"] + ".words.sorted"
    file["toms"] = file["path"] + ".toms.sorted"
    wordcommand = "cat %s | egrep \"^word \" | cut -d \" \" -f 2,3,4,5,6,7,8,9,10,11 | sort %s > %s" % (file["raw"],sortkeys,file["words"] )
    os.system(wordcommand)
    tomscommand = "cat %s | egrep -v \"^word \" | ./mktoms.py | sort -k 1,1n -k 2,2n -k 3,3n -k 4,4n > %s" % (file["raw"],file["toms"])
    os.system(tomscommand)
    
print "done sorting individual files."
wordfilearg = " ".join(file["words"] for file in fileinfo)
print "merging...this may take a while"

os.system("sort -m %s %s > %s" % (sortkeys,wordfilearg, workdir + "/all.words.sorted") )
os.system("sort -m -k 1,1n -k 2,2n -k 3,3n -k 4,4n %s > %s" % (" ".join(file["toms"] for file in fileinfo), workdir + "/all.toms.sorted") )
print "done merging.\nnow generating compression spec."

words = open(workdir + "/all.words.sorted")
testline = words.readline()
v = [0 for i in testline.split(" ")[1:]]
count = 0
freq = {}
word = ""
words.seek(0)
for line in words:
    count += 1
    word = line.split(" ")[0]
    try:
        freq[word] += 1
    except KeyError:
        freq[word] = 1
    fields = [int(i) for i in line.split(" ")[1:]]
    v = [i if i > v[e] else v[e] for e,i in enumerate(fields)]

print str(count) + " words total." 
print v

vl = [int(math.ceil(math.log(float(x),2.0))) if x > 0 else 1 for x in v]

print vl
width = sum(x for x in vl)
print str(width) + " bits wide."

hits_per_block = (blocksize * 8) // width
freq1 = index_cutoff
freq2 = 0
offset = 0

for word,f in freq.items():
    if f > freq2:
        freq2 = f
    if f < index_cutoff:
        pass
    else:
        blocks = 1 + f // (hits_per_block + 1)
        offset += blocks * blocksize

freq1_l = math.ceil(math.log(float(freq1),2.0))
freq2_l = math.ceil(math.log(float(freq2),2.0))
offset_l = math.ceil(math.log(float(offset),2.0))

print "freq1: %d; %d bits" % (freq1,freq1_l)
print "freq2: %d; %d bits" % (freq2,freq2_l)
print "offst: %d; %d bits" % (offset,offset_l)

dbs = open(workdir + "dbspec4.h","w")
print >> dbs, "#define FIELDS 9"
print >> dbs, "#define TYPE_LENGTH 1"
print >> dbs, "#define BLK_SIZE " + str(blocksize)
print >> dbs, "#define FREQ1_LENGTH " + str(freq1_l)
print >> dbs, "#define FREQ2_LENGTH " + str(freq2_l)
print >> dbs, "#define OFFST_LENGTH " + str(offset_l)
print >> dbs, "#define NEGATIVES {0,0,0,0,0,0,0,0,0}"
print >> dbs, "#define DEPENDENCIES {-1,0,1,2,3,4,5,0,0}"
print >> dbs, "#define BITLENGTHS {%s}" % ",".join(str(i) for i in vl)
dbs.close()
