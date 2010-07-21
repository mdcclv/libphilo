import HTMLParser
import Toms
import Query
import time
import re
import sys

TEIFormat = {"speaker":"\t",
			 "/speaker":":\n",
			 "head":"\n------\n",
			 "/head":"\n------\n",
			 "stage":"\n\t\t[",
			 "/stage":"]\n",
			 "/l":"\n",
			 "/ab":"\n",
			 "p":"\t",
			 "/p":"\n",
			 "pb":"\n---\n"}

class Formatter(HTMLParser.HTMLParser):
    def __init__(self, table = TEIFormat):
        self.buffer = ""
        self.table = table
    def format(self,data):
        self.buffer = ""
        self.reset()
        self.feed(data)
        #self.close() 
        #don't close()--croaks on EOF mid-event, which we should assume will happen.
        #instead, we just want to silently discard unparseable data.
        return self.buffer
    def handle_starttag(self,tag,attr):
        if tag in self.table:
            self.buffer += self.table[tag]
    def handle_endtag(self,tag):
        if "/" + tag in self.table:
            self.buffer += self.table["/" + tag]
    def handle_data(self,data):
        data = re.sub("^.*?>","",data,1)
        data = data.strip()
        self.buffer += data


if __name__ == "__main__":
	width = 600
	path = "/var/lib/philologic/databases/sha4test2"
	t = Toms.Toms(path + "/toms")
	q = Query.query(path,sys.stdin.readline().strip())
	f = Formatter()
	
	while not q.done:
		time.sleep(.05)
		q.update()
		
	for hit in q:
		meta = t[hit[0]]
		offset = hit[6]
		print "-------------"
		print meta["title"]
		print "-------------"
		file = open(path + "/TEXT/" + meta["filename"])
		left = max(0,offset - width)
		right = min(meta["end"],offset + width)
		length = right - left
		file.seek(left)
		content = file.read(length)
		file.close()
		formatted = f.format(content)
		print formatted
		
