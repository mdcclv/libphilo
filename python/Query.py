#!/usr/bin/env python
import sys
import os
import subprocess
import time
import struct
import HitList

def query(db,terms,n=1,corpus_file=None,corpus_size=0,method=None,method_arg=None):
	sys.stdout.flush()
	origpid = os.getpid()
	hfile = str(origpid) + ".hitlist"
	dir = "/var/lib/philologic/hitlists/"
	hl = open(dir + hfile, "w")
	err = open("/dev/null", "w")
	pid = os.fork()
	if pid == 0:
		os.umask(0)
		os.chdir(dir)
		os.setsid()
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
		else:
			#now we're detached from the parent, and can do our work.
			args = ["search4", db]
			if corpus_file and corpus_size:
				args.extend(("--corpusfile", corpus_file , "--corpussize" , str(corpus_size)))
			worker = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=hl,stderr=err)
			worker.communicate(terms)
			worker.stdin.close()
			worker.wait()
			#do something to mark query as finished
			flag = open(dir + hfile + ".done","w")
			flag.write(" ".join(args) + "\n")
			flag.close()
			sys.exit(0)
	else:
		hl.close()
		return HitList.HitList("/var/lib/philologic/hitlists/" + hfile,n)

def packbib(fmt,vals):
	buf = ""
	for i in vals:
		t = struct.pack(fmt,i)
		buf += t
	return buf
