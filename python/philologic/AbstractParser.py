from philologic.OHCOVector import *
import philologic.shlax as shlax
import re
import os
import philologic.Toms as Toms

class AbstractParser:
    def __init__(self,filename,docid):
        self.reader = None
        self.writer = None
        self.filename = filename
        self.context = []
        self.counts = {}
        self.metahandler = None
        self.objects = OHCOVector(["doc","div1","div2","div3","para","sent","word"])
        self.objects.v[0] = docid - 1
        self.objects_max = self.objects.v
        self.line_max = 0
        self.mapping = {"TEI":"doc",
                        "TEI.2":"doc",
                        "front":"div",
                        "div":"div",
                        "div0":"div",
                        "div1":"div",
                        "div2":"div",
                        "div3":"div",
                        "p":"para",
                        "sp":"para",
                        "stage":"para"}

        self.metamap = { "titleStmt/author" : "author",
                         "titleStmt/title" : "title",
                         "div/head" : "head",
                         "div1/head" : "head"}

        self.context_memory = None
        self.parallel = {"line":0,
                         "byte":0}

    def context_match(self,context,pattern):
        nodes = [x for x in pattern.split("/") if x != ""]
        for node in nodes:
            if node in context:
                position = context.index(node)
                context = context[position:]
            else:
                return False
        return True
        
    def push_object(self,type):
        self.objects.push(type)
        self.objects_max = [max(x,y) for x,y in zip(self.objects.v,self.objects_max)]
        #should maintain a toms stack here, basically.

    def pull_object(self,type):
        self.objects.pull(type)
        self.objects_max = [max(x,y) for x,y in zip(self.objects.v,self.objects_max)]
        #should remove toms from the stack and print them here.

    def parse(self, input, output):
        self.reader = input
        self.writer = output
        p = shlax.parser(self.reader)
        for n in p:
            if n.type == "StartTag":
                self.parallel["byte"] = n.start
                self.context.append(n.name)
                for pattern in self.metamap:
                    if self.context_match(self.context,pattern):
                        self.metahandler = self.metamap[pattern]
                        self.context_memory = self.context
                if n.name in self.mapping:
                    type = self.mapping[n.name]
                    self.push_object(type)
                    attlist = ""
                    for k,v in n.attributes.items():
                        attlist += " %s=\"%s\"" % (k,v)
                    try:
                        emit_object(self.writer,type,"<" + n.name + attlist + ">",self.objects.v,self.parallel["byte"],self.parallel["line"])
                    except UnicodeDecodeError:
                        print >> sys.stderr, "bad encoding at %s byte %s" % (self.filename,n.start)
                    if type == "doc":
                        print >> self.writer, "meta %s %s" % ("filename", self.filename)
                if n.name == "l":
                    if "n" in n.attributes.keys():
                        self.parallel["line"] = int(n.attributes["n"])
                    else:
                        self.parallel["line"] += 1
                    print >> self.writer, "line %d %d" % (self.parallel["byte"],self.parallel["line"])
                    self.line_max = max(self.parallel["line"],self.line_max)
            elif n.type == "EndTag":
                self.parallel["byte"] = n.start
                for pattern in self.metamap:
                    if self.context_memory and self.context_memory == self.context:
                        self.metahandler = None
                        self.context_memory = None
                try:
                    self.context.pop()
                except IndexError:
                    print >> sys.stderr, "mismatched tag at %s byte %s" % (self.filename,n.start)
                if n.name in self.mapping:
                    type = self.mapping[n.name]
                    self.pull_object(type)
                    emit_object(self.writer,type,"</" + n.name + ">",self.objects.v,self.parallel["byte"],self.parallel["line"])                           
            elif n.type == "text":
                self.parallel["byte"] = n.start
                try:
                    text = n.content.decode("UTF-8")
                    tokens = re.finditer(ur"([\w\u2019]+)|([\.;:?!])",text,re.U)
                    offset = self.parallel["byte"]
                    if self.metahandler:
                        cleantext = re.sub("[\n\t]"," ",text)
                        print >> self.writer, "meta %s %s" % (self.metahandler,cleantext)
                    for token in tokens:
                        if token.group(1):
                            self.push_object("word")
                            char_offset = token.start(1)
                            byte_length = len(text[:char_offset].encode("UTF-8"))
                            emit_object(self.writer,"word",token.group(1),self.objects.v,offset + byte_length,self.parallel["line"])                           
                            self.counts[token.group(1)] = self.counts.get(token.group(1),0) + 1
                        if token.group(2):
                            self.push_object("sent")
                            char_offset = token.start(1)
                            byte_length = len(text[:char_offset].encode("UTF-8"))
                            emit_object(self.writer,"sent",token.group(2),self.objects.v,offset + byte_length,self.parallel["line"])                           
                except UnicodeDecodeError:
                    print >> sys.stderr, "bad encoding in %s around byte %s" % (self.filename,n.start)
        #Here [after done parsing] I should see if I still have an object stack, and unwind it, if so.
        max_v = self.objects_max
        max_v.extend((self.parallel["byte"],self.line_max))
        return (max_v,self.counts)

#And a helper method.
def emit_object(destination, type, content, vector, *bonus):
    print >> destination, "%s %s %s %s" % (type,
                                           content,
                                           " ".join(str(x) for x in vector),
                                           " ".join(str(x) for x in bonus)
                                          )

if __name__ == "__main__":
    import sys
    did = 1
    files = sys.argv[1:]
    for docid, filename in enumerate(files):
        f = open(filename)
        o = codecs.getwriter('UTF-8')(sys.stdout)
        p = AbstractParser(filename,docid)
        spec,counts = p.parse(f,o)
        print "%s\n%d total tokens in %d unique types." % (spec,sum(counts.values()),len(counts.keys()))
