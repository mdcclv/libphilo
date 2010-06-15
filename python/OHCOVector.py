#!/usr/bin/python
import re
import os
import sys
import codecs


class OHCOVector:
	def __init__(self,levels):
		self.levels = levels

		self.v = []
		self.types = {} #maps literal levels onto hierarchical types.

		self.hier = []
		self.maxdepths = {} #the width of each hier type.  anything beyond is nested.

		self.currentdepths = {} # for hier types--from 1 up to max
		self.nesteddepths = {} # for hier types--only greater than 0 when current==max
		
		for i,lev in enumerate(levels):
			self.v.append(0)
			m = re.match(r"(.+)(\d+)$",lev)
			if m:
				type = m.group(1)
				n = m.group(2)
				self.types[lev] = lev
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
		depth = 0
		#if we have a verbatim type listed in self.levels,
		#we can calculate it's position directly.
		if otype in self.levels:
			depth = self.levels.index(otype)
			type = self.types[otype]
			order = self.hier.index(type)
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
		#pull really only makes sense for a hierarchical type, 
		#where we can keep a stack of how many elements currently exist.
		depth = 0
		if otype in self.levels:
			pass		
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
			self.v[depth] += 1
			for j in range(depth + 1,len(self.levels)):
				self.v[j]=0						
		return 0

	def __str__(self):
		r = []
		for l, n in zip(self.levels,self.v):
			r.append("%s:%d" % (l,n))
		return "(%s)" % ", ".join(r)
