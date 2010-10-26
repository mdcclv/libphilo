#!/usr/bin/env python

from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.SqlToms import SqlToms
from philologic.DirtyFormatter import Formatter
import urlparse
import re

classes = ['head', 'stage', 'l','ln', 'ab', 'speaker', 'pb']
myformat = {}
for c in classes:
    myformat[c] = "<span class='%s'>" % c
    myformat["/" + c] = "</span>"

myformat["p"] = "<p/>"
myformat["/p"] = ""
myformat["br"] = "<br/>"
myformat["span"] = "<span>"
myformat["/span"] = "</span>"

f = Formatter(myformat)

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
    print >> environ['wsgi.errors'], dbname
    if not dbname: return
    else:
        dbfile = "/var/lib/philologic/databases/" + dbname + "/toms.db"
    toms = SqlToms(dbfile,7)
    print >> environ['wsgi.errors'],"opened toms"
    obj = []
    count = 0

    while True:
        p = shift_path_info(environ)
        if p:
            obj.append(p)
        else:
            break
    yield "looking up %s" % str(obj)
    filename = ""
    start = 0
    end = 0
    length = 0
    for r in range(1,len(obj) + 1):
        parent = obj[:r]
        yield str(parent)
        if parent in toms:
            yield "retreiving %s" % repr(parent)
            o = toms[parent]
            filename = o["filename"] or filename
            start = o["start"] or start
            end = o["end"] or end
    yield repr((filename,length,start,end))
    file = "/var/lib/philologic/databases/%s/TEXT/%s" % (dbname,filename)
    fh = open(file)
    fh.seek(start)
    chunk = fh.read(end - start)
    if "word_offset" in environ["parsed_params"]:
        word_offset =  int(environ["parsed_params"]["word_offset"][0])
        if word_offset >= start and word_offset <= end:
            breakpoint = word_offset - start
            left = chunk[:breakpoint]
            rest = chunk[breakpoint:]
            word,right = re.split("[\s.;:,<>?!]",rest,1)    
            yield f.format(left + "<span rend='preserve' class='hilite'>" + word + "</span> " + right)
            return
    yield f.format(chunk)
#    yield left
#    yield word
#    yield right

if __name__ == "__main__":
    CGIHandler().run(simple_dispatch)
