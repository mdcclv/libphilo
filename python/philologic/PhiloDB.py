import os,sys
import hashlib
import struct
from philologic import Query,SqlToms,HitList

class PhiloDB:
    def __init__(self,dbpath,width = 7):
        self.path = dbpath
        self.toms = SqlToms.SqlToms(dbpath + "/toms.db",width)
        self.width = width

    def query(self,qs,method=None,method_arg=0,**metadata):
        hashable = (qs,method,method_arg,tuple(metadata.items()))
        hash = hashlib.sha1()
        hash.update(self.path)
        hash.update(qs)
        hash.update(method or "")
        hash.update(method_arg or "")
        for key,value in metadata.items():
            hash.update(key)
            hash.update(value)
        hex_hash = hash.hexdigest()
        print >> sys.stderr,"%s hashes to %s" % (hashable,hex_hash)
        #check here to see if the query is cached.
        hfile = "/var/lib/philologic/hitlists/" + hex_hash + ".hitlist"
        words_per_hit = len(qs.split(" "))
        if os.path.isfile(hfile):
            print >> sys.stderr, "%s cached already" % (hashable,)
            return HitList.HitList(hfile,words_per_hit) #debug.
        corpus_file = None
        corpus_size = self.width
        corpus_count = 0
        print >> sys.stderr, "metadata = %s" % repr(metadata)
        if metadata:
            corpus_file = "/var/lib/philologic/hitlists/" + hex_hash + ".corpus"
            corpus_fh = open(corpus_file,"wb")
            for c_obj in self.toms.query(**metadata):
                c_id = [int(x) for x in c_obj["philo_id"].split(" ")]
                corpus_fh.write(struct.pack("=7i",*c_id))
                corpus_count += 1
            corpus_fh.close()
            if corpus_count == 0: return []
        print >> sys.stderr, "%d metadata objects" % corpus_count
        return Query.query(self.path,qs,corpus_file,corpus_size,method,method_arg,filename=hfile)
        
    def compound_query(self,qs,method=None,method_arg=0,*metadata_dicts):
        hash = hashlib.sha1()
        hash.update(self.path)
        hash.update(qs)
        hash.update(method or "")
        hash.update(method_arg or "")
        for metadata_level in metadata_dicts:
            for k,v in metdata_level.items():
                hash.update(k)
                hash.update(v)
        hex_hash = hash.hexdigest()
        print >> sys.stderr, "('%s' %s %d %s )hashes to %s" % (qs,method,method_arg,repr(metadata),hex_hash)
        hfile = "/var/lib/philologic/hitlists/" + hex_hash + ".hitlist"
        words_per_hit = len(qs.split(" "))
        if os.path.isfile(hfile):
            print >> sys.stderr, "%s cached already" % (hashable,)
            return HitList.HitList(hfile,words_per_hit) #debug.
        corpus_file = None
        corpus_size = self.width
        corpus_count = 0
        print >> sys.stderr, "metadata = %s" % repr(metadata)
        if metadata:
            corpus_file = "/var/lib/philologic/hitlists/" + hex_hash + ".corpus"
            corpus_fh = open(corpus_file,"wb")
            for c_obj in self.toms.compound_query(*metadata):
                c_id = [int(x) for x in c_obj["philo_id"].split(" ")]
                corpus_fh.write(struct.pack("=7i",*c_id))
                corpus_count += 1
            corpus_fh.close()
            if corpus_count == 0: return []
        print >> sys.stderr, "%d metadata objects" % corpus_count
        return Query.query(self.path,qs,corpus_file,corpus_size,method,method_arg,filename=hfile)

    def ancestors(self,object):
        """Analyze a single object id and return all objects that are direct ancestors of it."""
        print >> sys.stderr, object
        if isinstance(object,str) or isinstance(object,unicode):
            object = object.split(" ")
        elif "philo_id" in object:
            object = object["philo_id"].split(" ")
        r = []
        object = list(object)
        for n in range(1,len(object) + 1):
            print >> sys.stderr, r
            print >> sys.stderr, object
            ancestor = object[:(n)]
            ancestor.extend([0 for i in range(len(object) - n)])
            print >> sys.stderr, ancestor
            r.append(tuple(ancestor))
        return r