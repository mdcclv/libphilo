#!/usr/bin/env python
import cgi
import cgitb
import os
import sys
import re
import time
import struct

from libphilo import *

#Enable the CGI debugger.  Incredibly useful.
cgitb.enable()

#Analyze the CGI query parameters and path_info.
form = cgi.FieldStorage() #contains all '?key=value' pairs from the query

# I'm taking the database name from the CGI PATH_INFO variable.  
# This allows us to give each database a URI of the form .../cgi4.py/dbname
# With a script named "philologic.py" or some such it would be even slicker.

pathinfo = os.environ["PATH_INFO"] # contains the "extra" path after the script, before the params.
path_list = [i for i in pathinfo.split("/") if i != ""] # split and knock off the leading "/"
db = path_list.pop(0) # the first element is the dbname.  we'll use the rest later.

# Now find the db and open it.
dbp = "/var/lib/philologic/databases/" + db
t = Toms.Toms(dbp + "/toms") 

# all metadata is in one flat file for now.  We access it like a list of hashes, keyed by object id.

#Print out basic HTTP/HTML headers and container <div> elements.
print "Content-Type: text/html"
print
print '<html>\n<body style="background-color:grey">'
print '<div style="margin: 15px; padding:10px; width:800px;  \
                   background-color:white; border:solid black 3px; -moz-border-radius:5px; \
                   -webkit-border-radius:5px;">'
print "<div id=\"dbname\" style=\"text-align: center; font-weight:bold; font-size:large\">" + db + \
      "</div><hr/>"

# set up reasonable defaults.
qs = ""
metastring = ""
corpusfile = None
corpussize = 0
corpus = None

# parse the CGI query parameters.
if "query" in form:
    qs = form["query"].value

if "meta" in form:
    metastring = form["meta"].value
    corpus = Toms.toms_select(t,metastring)
	# we have to pack the corpus into a file of binary integers 
    corpussize = 7
    corpusfile = "/var/lib/philologic/hitlists/tmpcorpus"
    cfh = open(corpusfile,"w")
    for d in corpus:
        cfh.write(struct.pack("=7i",*d["id"])) #unpack the id list into discrete arguments to pack.
    cfh.close()

# print out a form.
print '<form action="%s"><table style="border:none">' % (os.environ["SCRIPT_NAME"] + "/" + db)
print '<tr><td>query:</td><td><input name="query" type="text" value="%s"/></td></tr>' % qs
print '<tr><td>meta:</td><td><input name="meta" type="text" value="%s"/></td></tr>' % metastring
print '</table><input type="submit"/></form>'

if path_list:
	object = [int(x) for x in path_list]
	filename = dbp + "/TEXTS/" + t[object[0]]["filename"]
	meta = t[object]
	text = Query.get_object(filename,int(meta["start"]),int(meta["end"]))
	print "<pre>" + text + "</pre>"
	print '</div></body></html>'
	exit()
# go execute the query.
q = Query.query(dbp,qs,corpusfile,corpussize)

# wait for it to finish.  not strictly necessary.  
# could wait until we have 50 results, then print those.
while not q.done:
    time.sleep(.05)
    q.update()

print "<hr/>" + str(len(q)) + " results.<br/>"
    
# print out all the results.    
for hit in q:
    doc = t[hit[0]] # look up the document in the toms.
    filename = doc["filename"]
    path = dbp + "/TEXTS/" + filename
    file_length = doc["end"]
    offset = hit[6] # I should abstract the actual positions of document, byte, etc.
    buf = Query.get_context(path,offset,file_length,500)

    print "%s,%s : %s" % (doc["title"],doc["author"],doc["filename"])

	#Ugly metadata formatting.
    i = 2
    while i <= 4:
        if hit[i -1] > 0:
            try :
                div = t[hit[:i]]
                if "head" in div:
                    print "<a href=\"" + (os.environ["SCRIPT_NAME"] + "/" + db + "/" + "/".join(str(x) for x in hit[:i])) + "\">" + div["head"] + "</a>, "
            except IndexError:
                pass
        i += 1

    print " : <div style='margin-left:40px; margin-bottom:10px; font-family:monospace'>" + buf + "</div>"

print '</div></body></html>'
