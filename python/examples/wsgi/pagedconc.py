#!/usr/bin/env python
import cgi
import cgitb
import sys
import tempfile
from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
import urlparse
import re
import time
import struct

from philologic import *
from philologic.SqlToms import SqlToms
from philologic.PhiloDB import PhiloDB
def get_raw_context(file,offset,file_length,width):
    lo = max(0,offset - width)
    breakpoint = offset - lo
    ro = min(file_length, offset + width)

    fh = open(file)
    fh.seek(lo)
    buf = fh.read(ro - lo)
    lbuf = buf[:breakpoint]
    rbuf = buf[breakpoint:]
    (word,rbuf) = re.split("[\s.;:,<>?!]",rbuf,1)
    fh.close()
    return (lbuf,word,rbuf)

def format_object(row,script):
    r = "<span class='philo_object' type='%s' href='%s'>" % (row["philo_type"],script + "/" + "/".join(row["philo_id"].split(" "))) 
#    r += "<span class='philo_type'>" + row["philo_type"] + "</span> "
#    r += "<span class='philo_id'>" + row["philo_id"] + "</span> " # accidentally included the trailing space.  stupid regex mistake.
    if row["filename"]:
        r += "<span class='philo_filename'>" + str(row["filename"]) + "</span> "
    if row["title"]:
        r += "<span class='philo_title'>" + str(row["title"]) + "</span> "
    if row["author"]:
        r += "<span class='philo_author'>" + str(row["author"]) + "</span> "
    if row["head"]:
        r += "<span class='philo_head'>" + str(row["head"]) + "</span> "
    return r + "</span>\n"

def simple_dispatch(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    # a wsgi app is supposed to return an iterable;
    # yielding lets you stream, rather than generate everything at once.
    # yield repr(environ)
    dbname = shift_path_info(environ)
    myname = environ["SCRIPT_NAME"]
    if not dbname: return
    dbpath = "/var/lib/philologic/databases/" + dbname
    db = PhiloDB(dbpath,7)
    toms =  db.toms
    obj = []
    count = 0
    corpus_file = None
    corpus_size = 7
    corpus_count = 0
    if "meta1field" in environ["parsed_params"] and environ["parsed_params"]["meta1field"][0] and "meta1" in environ["parsed_params"] and environ["parsed_params"]["meta1"][0]:
        c_field = environ["parsed_params"]["meta1field"][0]
        c_value = environ["parsed_params"]["meta1"][0]
        meta_dict = {c_field:c_value}
    else:
        meta_dict = {}
    if "query" in environ["parsed_params"]:
        qs = environ["parsed_params"]["query"][0]
        q_start = int(environ["parsed_params"].get('q_start',[0])[0]) or 0
        q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 50        
        f = Formatter.Formatter({})

        yield "<html><body><div class='conc_response'>running query for '%s'<br/>" % qs 
        print >> environ["wsgi.errors"], str(corpus_file)

        q = db.query(qs,**meta_dict)

        while len(q) <= q_end and not q.done:
            time.sleep(.05)
            q.update()
        l = len(q)
        yield "<div class='status' n=%d%s>%d hits</div>" % (l," done='true'" if q.done else "", l)
        
        yield "<div class='results'>"
        for hit in q[q_start:q_end]:
            context_file = ""
            context_file_end = 0
            rstr = ""
            yield "<div class='hit' id='%s' offset=%d>" % ("/".join(str(x) for x in hit[:6]),hit[6])

            #get the metadata for all unique parents of the hit.
            for i in range(1,len(hit)):
                hit_parent = hit[:i]
                if hit[i-1] == 0:
                    continue
                if hit_parent in toms:
                    parent = toms[hit_parent]
                    rstr += format_object(parent,"")
                    if parent["filename"]:
                        context_file = parent["filename"]
                        context_file_end = parent["end"]

            yield "<span class='cite'>" + rstr + "</span>"
            path = dbpath + "/TEXT/" + context_file
            offset = hit[6] #dangerous...
            (left,word,right) = get_raw_context(path,offset,context_file_end,250)
            (left,word,right) = [f.format(x) for x in (left,word,right)]
            content = "<span class='left'>%s</span> <span class='word'>%s</span> <span class='right'>%s</right>" % (left,word,right)
            yield "<span class='content'>%s</span>" % content
            yield "</div>"
            count += 1

        yield "</div>%d hits" % count 
        yield "</div></body></html>"

if __name__ == "__main__":
    CGIHandler().run(simple_dispatch)
