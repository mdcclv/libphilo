#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
import cgitb
cgitb.enable()
import urlparse
import sys
from philologic.SqlToms import SqlToms
obj_width = 7

def simple_dispatch(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    # a wsgi app is supposed to return an iterable;
    # yielding lets you stream, rather than generate everything at once.
#    yield repr(environ)
    dbname = shift_path_info(environ)
    myname = environ["SCRIPT_NAME"]
    if not dbname: return
    else:
    	dbfile = "/var/lib/philologic/databases/" + dbname + "/toms.db"
    print >> sys.stderr, dbfile
    toms = SqlToms(dbfile,7)
    obj = []
    count = 0

    while True:
        p = shift_path_info(environ)
        if p:
            obj.append(p)
        else:
            break
    if obj:
        for chunk in toms.get_children(obj):
            yield format_object(chunk,myname) + "<br/>"
            count += 1
    elif environ["parsed_params"]:
        qdict = {}
        for k in environ["parsed_params"]:
            qdict[k] = environ["parsed_params"][k][0]
        for object in toms.query(**qdict):
            yield format_object(object,myname) + "<br/>"
            count += 1
    else:
        for chunk in toms.get_documents():
            yield format_object(chunk,myname) + "<br/>"
            count += 1
    yield str(count) + " objects."

def format_object(row,script):
    r = "<a class='philo_object' href='%s'>" % (script + "/" + "/".join(row["philo_id"].split(" "))) 
    r += "<span class='philo_type'>" + row["philo_type"] + "</span> "
    r += "<span class='philo_id'>" + row["philo_id"] + "</span> " # accidentally included the trailing space.  stupid regex mistake.
    if row["title"]:
        r += "<span class='philo_title'>" + str(row["title"]) + "</span> "
    if row["author"]:
        r += "<span class='philo_author'>" + str(row["author"]) + "</span> "
    if row["head"]:
        r += "<span class='philo_head'>" + str(row["head"]) + "</span> "
    return r + "</a>\n"

if __name__ == "__main__":
    CGIHandler().run(simple_dispatch)
    
