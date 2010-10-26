#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
import urlparse

template = """
<html>
<head>
<style type="text/css">
span.l{
    display:block;
}
span.ab{
    display:block;
}
span.ln{
	display:block;
}
span.speaker {
    display: block;
    font-weight:bold;
    margin-left:-10px;
}
span.stage {
    display: block;
    font-style:italic;
    margin-left: 20px;
}
span.head {
	display: block;
	font-weight:bold;
	margin: 10px 0px 10px 0px
}
span.kwichilite {
	font-weight:bold;
}
#context span.hilite {
	font-weight:bold;
	border-bottom:solid 1px red;
}
#concordance span.hilite {
	font-weight:bold;
	color:black;
}
#concordance span.content:hover {
	border-bottom:solid 1px red;
}
#concordance span.cite:hover {
	color:red;
}
.hit {
	font-family:monospace;	
}
span.philo_type {
	display:none;
}
span.philo_id {
	display:none;
}
span.philo_author {
	display:none;
}
span.philo_title {
	display:none;
}
span.philo_head {
	display:none;
}
span.popup_bib {
	display:block;
}
.toc_display{
	display:inline;
}
span.moreconc:hover {
	color:red;
}
div#toc span.philo_object span.philo_author {
    display:inline;
}
div#toc span.philo_object span.philo_title {
    display:inline;
}
span.popup_container {
	display:block;
	position:absolute;
	margin-left:30px;
	z-index:1;
	background-color:#EAEEEE;
	border: solid 1px #888888;
	color:black;
}
</style>

<script type="text/javascript" src="/jquery-1.4.2.min.js"></script>
<script type="text/javascript">
    var concsource = "/cgi-bin/wsgitest/pagedconc.py/%(dbname)s/";
    var tocsource = "/cgi-bin/wsgitest/toc.py/%(dbname)s/";
    var contextsource = "/cgi-bin/wsgitest/context.py/%(dbname)s/";
	var intervalID = 0;
	var concposition = 0;
	var concsize = 50;
	
	function place_kwic(index,element){
	  $(element).prepend((concposition + 1) + ") ");
	  concposition += 1;
	  $("#concordance").append(element);
	  newElement = $("#concordance > .hit").last();
	  $(".word",newElement).addClass("hilite");
	  left = $(".left",newElement);
	  left_words = left.text().split(" ").filter(function(x){return x;});	  
	  right = $(".right",newElement);
	  right_words = right.text().split(" ").filter(function(x){return x;});
	  while (left.width() > 300 ) {
		left_words = left_words.slice(1);
		left.text(left_words.join(" "));
	  }
	  while (right.width() > 300 ) {
		right_words = right_words.slice(0,-2);
		right.text(right_words.join(" "));
	  }
	  currentwordoffset = $(".word",newElement).offset()["left"];
	  if (currentwordoffset < 650) {
		offsetchange = 650 - currentwordoffset;
		$(".content",newElement).offset({"left": $(".content",newElement).offset()["left"] + offsetchange});
	  }
	};	
	
	function pop_and_format(q){
		element = q.shift()
		if (!(element)){
			clearInterval(intervalID);
		}
		else {
			place_kwic(0,element);
		}
	};
    $(document).ready(function(){
      $("#concform").submit(function(){
	    $("#status").html("retrieving...");
		$("#more").html();
		$("#toc").hide();
		$("#context").hide();
        $("#concordance").text("");
		$("#concordance").show();
        hit_queue = [];
        qval = $("#concform").serialize();
        $.get(concsource, qval, function(data,status,request){
          myresponse = data;
          myparsedresponse = $(data);
          count = 0;
          mystatus = $(".status",myparsedresponse);
          last = mystatus.attr("n");	
          $("#status").html(mystatus);
          if (!(mystatus.attr("done"))){
            $("#status").append("still working...");
          }
		  $("div.hit",myparsedresponse).each(function(index,value){
		  	hit_queue.push(value);  
		  	count += 1;
		  });
		  intervalID = setInterval("for (i=0;i<10;i++){pop_and_format(hit_queue);}",30);
		  concposition = 0;
		  if (count == concsize) {
		  	q_start = concposition + concsize;
		  	q_end = concposition + concsize + concsize;
		  	morebutton = "<br/><span class='moreconc' start=" + q_start + " end=" + q_end + ">More</span>";
		    $("#more").html(morebutton);
		  }
        });
      	return false;
      });
      $("body").delegate("span.moreconc","click",function() {
		$("#more").append("...retrieving");
		page_params = $.param({"q_start":q_start,"q_end":q_end});
		more_params = qval + "&" + page_params;
        $.get(concsource, more_params, function(data,status,request){
		  $("#toc").hide();
		  $("#context").hide();
		  $("#concordance").text("");
		  $("#concordance").show();
  		  hit_queue = [];
          myresponse = data;
          myparsedresponse = $(data);
          count = 0;
          mystatus = $(".status",myparsedresponse);
          last = mystatus.attr("n");	          
          $("#status").html(mystatus);
          if (!(mystatus.attr("done"))){
            $("#status").append("still working...");
          }

		  $("div.hit",myparsedresponse).each(function(index,value){
		  	hit_queue.push(value);  
		  	count += 1;
		  });
		  intervalID = setInterval("for (i=0;i<10;i++){pop_and_format(hit_queue);}",30);
		  concposition = q_start;
		  if (count == concsize) {
		  	q_start = concposition + concsize;
		  	q_end = concposition + concsize + concsize;
		  	morebutton = "<br/><span class='moreconc' start=" + q_start + " end=" + q_end + ">More</span>";
		    $("#more").html(morebutton);
		  }
		  else {
		  	$("#more").html("");
		  }
		});
      });
      $("body").delegate("span.cite",'mouseover', function() {
		$(".popup_container",$(this)).detach()
		mycite = $(this).clone();
		mycite.addClass("popup_container")
		parent = $(this).parents(".hit");
		$("span",mycite).addClass("popup_bib");
		$(this).append(mycite);
      });
      $("body").delegate("span.cite","mouseout",function() {
      	$(".popup_container",$(this)).detach()      
      });
      $("body").delegate("span.philo_object","click",function() {
      	var id_str = $("span.philo_id",$(this)).text();
      	var id_uri = id_str.split(" ").join("/");
      	$.get(contextsource + id_uri,"",function(data,status,request){
      		mycontextresponse = $(data);
      		$("#toc").hide();
      		$("#concordance").hide();
      		$("#context").text("");
      		$("#context").show();
      		$("#context").html(mycontextresponse);
      	
      	});        
      });
      $("body").delegate("span.cite","click",function() {
		var doc = $(".philo_object",$(this)).attr("href");
      	$.get(tocsource + doc,"",function(data,status,request){
      		mytocresponse = $(data);
      		mytocresponse.children().each(function(index,value){
      			$(value).css("display","inline");
      		});
      		$("#concordance").hide();
      		$("#context").hide();
      		$("#toc").show().html(mytocresponse);
      	});
      });
      $("body").delegate(".hit .content","click",function() {
      	hit_parent = $(this).parents(".hit");
		uri = hit_parent.attr("id");
      	offset = hit_parent.attr("offset");
		$.get(contextsource + uri,{"word_offset":offset},function(data,status,request){
		  myhitcontextresponse = $(data);
		  $("#toc").hide();
		  $("#concordance").hide();
		  $("#context").text("");
		  $("#context").show();
		  $("#context").html(myhitcontextresponse);		
		  $(window).scrollTop($(".hilite",$("#context")).position()["top"] - 300);

		});
      });      
    });        
    </script>
    </head>
<body style="background-color:#E8E8E8">
<div style="margin: 15px; padding:10px; width:1000px;                     background-color:white; border:solid black 3px; -moz-border-radius:5px;                    -webkit-border-radius:5px;">
<div id="dbname" style="text-align: center; font-weight:bold; font-size:large">%(dbname)s</div><hr/>

<form id="concform" action="/cgi-bin/wsgitest/pagedconc.py/%(dbname)s/">
<table style="border:none">
<tr><td>query:</td><td><input id="concquery" name="query" type="text" value=""/></td></tr><tr>
<td>meta:</td><td><input id="concmeta" name="meta1" type="text" value=""/> in <select name="meta1field"><option value=""></option>
<option value="author" >author</option>
<option value="title" >title</option>
<option value="head" >head</option>
<option value="filename" >filename</option>

</td></tr></table><input type='submit'/></form>
<div id="status"></div>
<hr/>
<div id="toc" style="margin:auto;"></div>
<div id="context" style="margin:auto;"></div>
<div id="concordance" style="margin:auto;"></div>
<hr/>
<div id="more" style="margin:auto;"></div>
</div>
</body>
</html>
"""

def simple_dispatch(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    # a wsgi app is supposed to return an iterable;
    # yielding lets you stream, rather than generate everything at once.
    # yield repr(environ)
    dbname = shift_path_info(environ)
    myname = environ["SCRIPT_NAME"]
    if not dbname: return
    else:
        yield template % {"dbname":dbname}

if __name__ == "__main__":
    CGIHandler().run(simple_dispatch)
