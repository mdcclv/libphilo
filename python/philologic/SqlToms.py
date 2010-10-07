import re
import os
import sys
import ast
import sqlite3

class SqlToms:
    def __init__(self,dbfile,w):
        self.dbh = sqlite3.connect(dbfile)
        self.dbh.text_factory = str
        self.dbh.row_factory = sqlite3.Row
        self.width = w

    def query(self,**args):
        if not args:
            return
        else:
            qstring = "SELECT * FROM toms WHERE"
            vs = []
            for k,v in args.items():
                qstring += " %s LIKE ?" % (k) # forgot the AND
                vs.append("%" + v + "%")
            qstring += " ORDER BY philo_seq;"
            print >> sys.stderr, qstring
            c = self.dbh.cursor()
            c.execute(qstring,vs)
            for row in c:
                yield row

    def get_documents(self):
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE philo_type='doc' ORDER BY philo_seq;")
        for row in c:
            yield row

    def get_children(self,obj):
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE parent=?;",(obj,))
        for row in c:
            yield row
                
    def mktoms_sql(file_in,sql_out):
        known_fields = []
        db = sqlite3.connect(sql_out)
        db.text_factory = str
        db.execute("CREATE TABLE IF NOT EXISTS toms (philo_type,philo_name,philo_id,philo_seq);")
        s = 0
        for line in open(file_in):
            (philo_type,philo_name,rest) = line.split("\t")
            fields = rest.split(" ",9)
            if len(fields) == 10: 
                philo_id = " ".join(fields[:7])
                raw_attr = fields[9]
                print raw_attr
                r = {}
                r["philo_type"] = philo_type
                r["philo_name"] = philo_name
                r["philo_id"] = philo_id
                r["philo_seq"] = s
                # I should add philo_parent here.  tricky to keep track of though.
                attr = ast.literal_eval(raw_attr)
                for k in attr:
                    if k not in known_fields:
                        print k
                        db.execute("ALTER TABLE toms ADD COLUMN %s;" % k) 
                        # it seems like i can't safely interpolate column names. ah well.
                        known_fields.append(k)
                    r[k] = attr[k]
                rk = []
                rv = []
                for k,v in r.items():
                    rk.append(k)
                    rv.append(v)
                ks = "(%s)" % ",".join(x for x in rk)
                print ks
                print repr(rv)
                insert = "INSERT INTO toms %s values (%s);" % (ks,",".join("?" for i in rv))
                db.execute(insert,rv)
                s += 1
        db.commit()
		
def obj_cmp(x,y):
	for a,b in zip(x,y):
		if a < b:
			return -1
		if a > b:
			return 1
	else:
		return 0

def obj_contains(x,y):
	pass

if __name__ == "__main__":
	import sys
	mktoms_sql(sys.argv[1],sys.argv[2])
	
