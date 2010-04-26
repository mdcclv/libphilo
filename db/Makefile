# $Id: Makefile.in,v 1.2 2004/05/28 19:22:11 o Exp $
CC= gcc
PH_CFLAGS= -I.. -I../../search-engine 
CFLAGS=
CPPFLAGS=
LDFLAGS= 
PH_LDMODULEFLAGS=-shared
PH_FPIC=-fPIC
all: unpack.o db.o bitsvector.o

validate-index: validate-index.c unpack.o bitsvector.o getresource.o
	$(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -o validate-index validate-index.c unpack.o bitsvector.o getresource.o -lgdbm

clean: 
	rm -f *.o *.lo libunpack_e.bundle *~ validate-index