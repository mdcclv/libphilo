// $Id: retreive.h,v 2.11 2004/05/28 19:22:06 o Exp $
// philologic 2.8 -- TEI XML/SGML Full-text database engine
// Copyright (C) 2004 University of Chicago
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the Affero General Public License as published by
// Affero, Inc.; either version 1 of the License, or (at your option)
// any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// Affero General Public License for more details.
// 
// You should have received a copy of the Affero General Public License
// along with this program; if not, write to Affero, Inc.,
// 510 Third Street, Suite 225, San Francisco, CA 94107 USA.


/* retreive.h: header file for the hit retreival subsystem */

#ifdef RETREIVE_H
  #error "retreive.h multiply included"
#else
  
  #define RETREIVE_H

  #ifndef C_H
    #include "c.h"
  #endif

  #ifndef SEARCH_H
    #include "search.h"
  #endif

  #define RETR_BLK_OK                       0
  #define RETR_BLK_CLEAN                    1
  #define RETR_HITS_CACHED                  2
  #define RETR_END_OF_MAP                   4
  #define RETR_RESMAP_FULL                  8
  #define RETR_BUMMER                      16
  #define RETR_REACHED_NEXT_BLOCK_BOUNDARY 32


  extern N32 retreive_hits ( Search s, N level, Gmap, Gmap ); 

#endif
