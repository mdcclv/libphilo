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

df = DynamicForm.validate(form)

# Now find the db and open it.
dbp = "/var/lib/philologic/databases/" + db
t = Toms.Toms(dbp + "/toms") 

# all metadata is in one flat file for now.  We access it like a list of hashes, keyed by object id.

#Print out basic HTTP/HTML headers and container <div> elements.
print "Content-Type: text/html; charset=utf-8"
print
print '<html>'
print '<head>' + DynamicForm.getjs() + '</head>'
print '<body style="background-color:grey">'
print df
print '<div style="margin: 15px; padding:10px; width:800px;  \
                   background-color:white; border:solid black 3px; -moz-border-radius:5px; \
                   -webkit-border-radius:5px;">'
print "<div id=\"dbname\" style=\"text-align: center; font-weight:bold; font-size:large\">" + db + \
      "</div><hr/>"

# set up reasonable defaults.

corpusfile = None
corpussize = 0
corpus = None

# parse the CGI query parameters.
if len(df["meta"]) > 0:
    corpus = [obj for obj in t if DynamicForm.formmatch(df,obj)]
    corpussize = 7
    corpusfile = "/var/lib/philologic/hitlists/tmpcorpus"
    cfh = open(corpusfile,"w")
    for d in corpus:
        print repr(d["id"]) + "<br/>"
        cfh.write(struct.pack("=7i",*d["id"])) #unpack the id list into discrete arguments to pack.
    cfh.close()

# print out a form.
print DynamicForm.generate(df,db)

# if we still have more path, we should just display an object and quit.
if path_list:
    object = [int(x) for x in path_list]
    filename = dbp + "/TEXT/" + t[object[0]]["filename"]
    meta = t[object]
    text = Query.get_object(filename,int(meta["start"]),int(meta["end"]))
    print "<pre>" + text + "</pre>"
    print '</div></body></html>'
    exit()

if corpus == []:
    print "no matching text objects."
    print '</div></body></html>'
    exit()

# otherwise, go execute the query.
q = Query.query(dbp,df["query"],corpusfile,corpussize)

# wait for it to finish.  not strictly necessary.  
# could wait until we have 50 results, then print those.
while not q.done:
    time.sleep(.05)
    q.update()

print "<hr/>" + str(len(q)) + " results.<br/>"

# print out all the results.    
for hit in q:
    print hit
    doc = t[hit[0]] # look up the document in the toms.
    filename = doc["filename"]
    path = dbp + "/TEXT/" + filename
    file_length = doc["end"]
    offset = hit[6] # I should abstract the actual positions of document, byte, etc.
    buf = Query.get_context(path,offset,file_length,500)

    print "%s,%s : %s" % (doc["title"],doc["author"],doc["filename"])

    #Ugly metadata/link formatting.
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
