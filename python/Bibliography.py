import re
import os
import sys

class Bibliography(object):
        def __init__(self,filename, *tags):
                self.filename = filename
                self.fh = open(self.filename)
                self.line = self.fh.readline()
                self.pos = 0
                self.tags = tags
	
        def __getitem__(self,n):
                if n > self.pos:
                        self.rewind()
                while self.pos < n:
                        self.line = self.fh.readline()
                        self.pos += 1
                        if self.line == "":
                                self.rewind()
                                raise IndexError
                return self.line.rstrip().split("\t")
		
        def __iter__(self):
                i = 0
                self.rewind()
                while True:
                        try: 
                                x = self[i]
                        except IndexError:
                                raise StopIteration
                        yield x
                        i += 1
			
			
        def __str__(self):
                r = "["
                for i in self:
                        r += str(i)
                        r += ","
                r = r[:-1] + "]"
                return r

        def rewind(self):
                self.fh.seek(0)
                self.line = self.fh.readline()
                self.pos = 0
	
        def printrow(self,i):
                return ". ".join(x for x in i if len(x) > 0)
