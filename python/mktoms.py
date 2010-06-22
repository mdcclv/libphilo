#!/usr/bin/env python
import re
import sys
stack = []

def printhelper(item):
	output = ""
	id = item.pop("id")
	output += " ".join(id)
	for key,value in item.items():
		output += "\t%s\t%s" % (key,value)
	print output

for line in sys.stdin:
	(type,rest) = line.strip().split(" ",1)
	tagmatch = re.match(r"<([^/>]+?.*?)>|</(.+?)>",rest)
	if tagmatch:
		object = [x for x in rest[tagmatch.end(0):].split(" ") if x != ""]
		id = object[:7]
		byte = object[7]
		if tagmatch.group(1):
			tagtext = tagmatch.group(1)
			if " " in tagtext:
				(name,att) = tagtext.split(" ",1)
			else:
				name = tagtext
			stack.append({"id":id,"type":type,"name":name,"start":byte})
		elif tagmatch.group(2):
			item = stack.pop()
			item["end"] = byte
			if item["type"] != "para": 
				printhelper(item)
	elif type == "meta":
		(type,name,value) = line.strip().split(" ",2)
		if name not in stack[-1]:
			stack[-1][name] = value
			
