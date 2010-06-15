#!/usr/bin/env python
import cgi
import cgitb
import os
import Query
import sys
import re
import time
import Bibliography
import philo3to4

cgitb.enable()

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print '<html>\n<body style="background-color:grey">'
print '<div style="margin: 15px; padding:10px; width:800px; background-color:white; border:solid black 3px; -moz-border-radius:5px; -webkit-border-radius:5px;">'
try: pathinfo = os.environ["PATH_INFO"]
except KeyError:
    pathinfo = ""
form = cgi.FieldStorage()

db = ""

if "db" in form:
    db = form["db"].value
    dbp = "/var/lib/philologic/databases/" + db
    bfile = "/bibliography"
    b = Bibliography.Bibliography(dbp + bfile)

docstring = ""
docfile = None
docsize = 0
docs_selected = None

if "doc" in form:
    docstring = form["doc"].value
    docs_selected = set()
    for d in b:
        for field in d:
            if re.search(docstring,field):
                docs_selected.add(int(d[20]))
    docsize = 1
    docfile = "/var/lib/philologic/hitlists/tmpcorpus"
    dfh = open(docfile,"w")
    dfh.write(Query.packbib("=i",docs_selected))
    dfh.close()

qstring = ""
qs = ""
q = []

if "query" in form:
    if not db:
        raise Error
    qstring = form["query"].value
    q = [level.split("|") for level in qstring.split(" ") ]
    qs = ""
    for level in q:
        for token in level:
            qs += token + "\n"
        qs += "\n"
    qs = qs[:-1] # to trim off the last newline.  just a quirk.

print '<form action="%s"><table style="border:none">' % os.environ["SCRIPT_NAME"]
print '<tr><td>db:</td><td><input name="db" type="text" value="%s"/></td></tr>' % db
print '<tr><td>query:</td><td><input name="query" type="text" value="%s"/></td></tr>' % qstring
print '<tr><td>doc:</td><td><input name="doc" type="text" value="%s"/></td></tr>' % docstring
print '</table><input type="submit"/></form>'

q = Query.query(dbp,qs,len(q),docfile,docsize)

while not q.done:
    #print "query not yet finished. sleeping .05 seconds.<br/>"
    time.sleep(.05)
    q.update()
        
print "<hr/>" + str(len(q)) + " results.<br/>"
    
for hit in q:
    filename = b[hit[0]][18]
    filelength = b[hit[0]][19]
    offset = hit[6]
    lo = max(0,offset - 250)
    ro = min(filelength, offset + 250)

    print b.printrow(b[hit[0]]) + " @ " + str(offset)
    path = dbp + "/TEXTS/" + filename
    fh = open(path)
    fh.seek(lo)
    buf = fh.read(ro - lo)
    buf = re.sub(r"^[^<]*>|^\w+\s|<.*?>|<[^>]*$|\s\w+$","",buf)
    print " : <div style='margin-left:40px; margin-bottom:10px'>" + buf + "</div>"
    fh.close()

if not docs_selected:
    docs_selected = [int(i[20]) for i in b]

print "<hr/>"

for i in b:
    if int(i[20]) in docs_selected:
        print b.printrow(i)
        print "<br/>"
print '</div></body></html>'
