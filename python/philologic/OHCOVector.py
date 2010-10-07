#!/usr/bin/python
import re
import os
import sys
import codecs


class OHCOVector:
    def __init__(self,levels):
        self.levels = levels # raw_hierarchy? INNERTYPES

        self.v = []
        self.types = {} #maps literal levels onto hierarchical types. # TYPEMAP?

        self.hier = [] #OUTERTYPES
        self.maxdepths = {} #the width of each hier type.  anything beyond is nested. #OUTERMAXDEPTH
        
        self.currentdepths = {} # for hier types--from 1 up to max #OUTERCURRENTDEPTH
        self.nesteddepths = {} # for hier types--only greater than 0 when current==max OUTERNESTEDDEPTH
        
        for i,lev in enumerate(levels):
            self.v.append(0)
            m = re.match(r"(.+)(\d+)$",lev)
            if m:
                type = m.group(1)
                n = m.group(2)
                self.types[lev] = type
                if type not in self.hier:
                    self.hier.append(type)
                self.maxdepths[type] = int(n)
                self.currentdepths[type] = 1
                self.nesteddepths[type] = 0
            elif re.match(r"(.+)$",lev):
                type = lev
                self.types[lev] = type
                self.maxdepths[lev] = 1 
                self.currentdepths[type] = 1
                self.nesteddepths[type] = 0
                self.hier.append(type)
            else:
                sys.stderr.write("bad vector definition\n")
                
    def push(self,otype):
        """handles the start of an object.  recursive types are special."""
        depth = 0
        #if we have a verbatim type listed in self.levels,
        #we can calculate it's position directly.
        if otype in self.levels:
            depth = self.levels.index(otype)
            type = self.types[otype]
            order = self.hier.index(type) # oo bad.
            current = depth + 1
            for htype in self.hier[:order]:
                for k in range(self.maxdepths[htype]):
                    current -= 1
            self.currentdepths[type] = current
        #if we have a hierarchical type listed in self.hier,
        #we have to walk through the hierarchy, and check the stack,
        #to find the correct position
        elif otype in self.hier:
            d = self.hier.index(otype)
            for htype in self.hier[:d]:
                for i in range (self.maxdepths[htype]):
                    depth += 1
            for j in range(1,self.currentdepths[otype]):
                depth += 1
            if self.currentdepths[otype] < self.maxdepths[otype]:
                self.currentdepths[otype] += 1
            else:
                self.nesteddepths[otype] += 1

        self.v[depth] += 1
        for j in range(depth + 1,len(self.levels)):
            self.v[j]=0
        return 0

    def pull(self,otype):
        depth = 0
        if otype in self.levels:
            depth = self.levels.index(otype)
            r = [i if n <= depth else 0 for n,i in enumerate(self.v)]
        elif otype in self.hier:
            d = self.hier.index(otype)
            for htype in self.hier[:d]:
                for i in range (self.maxdepths[htype]):
                    depth += 1
            for j in range(self.currentdepths[otype]):
                depth += 1
            if self.nesteddepths[otype] > 0:
                self.nesteddepths[otype] -= 1
            else:
                self.currentdepths[otype] -= 1
            r = [i if n <= depth else 0 for n,i in enumerate(self.v)]
            self.v[depth] += 1
            self.v = [j if n <= depth else 0 for n,j in enumerate(self.v)]
#           for j in range(depth + 1,len(self.levels)):
#               self.v[j]=0thank
        return r

    def currentdepth(self):
        d = len(self.v)
        while d >= 0:
            d -= 1
            if self.v[d] != 0:
                return d

    def typedepth(self,type):
        if type in self.levels: #levels should become inner_types
            return self.levels.index(type)
        elif type in self.hier: #hier should become outer_types
            d = 0
            for t in self.hier[:self.hier.index(type)]:
                d += self.maxdepths[t]
            d += self.currentdepths[type]
            return d
    
    def __str__(self):
        r = []
        for l, n in zip(self.levels,self.v):
            r.append("%s:%d" % (l,n))
        return "(%s)" % ", ".join(r)
