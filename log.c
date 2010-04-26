// $Id: log.c,v 2.11 2004/05/28 19:22:06 o Exp $
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

#include <stdio.h>
#include "c.h"
#include "log.h"

void s_log_msg ( char* format, Z8* message )
{
  if ( format )
    {
      fprintf (stderr, format, (char *)message); 
      fprintf (stderr, "\n");
    }
  else
    fprintf (stderr, "%s\n", (char *)message); 

}

void s_log ( Z32 debug_level, Z32 info_level, char* format, Z8* message )
{
  if ( (debug_level & info_level) == L_ERROR )
    {
      fprintf (stderr, "ERROR:\t"); 
      s_log_msg (format, message); 
    }
  else if ( (debug_level & info_level) == L_INFO)
    {
      fprintf (stderr, "info:\t"); 
      s_log_msg (format, message); 
    }
}
