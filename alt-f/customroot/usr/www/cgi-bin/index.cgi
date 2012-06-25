#!/bin/sh

. common.sh

if test -n "$QUERY_STRING"; then		
	parse_qstring
	pg="$(httpd -d "$pg")"
fi

cat<<-EOF
	Content-Type: text/html; charset=UTF-8

	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	<html><head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<style type="text/css">
	p.Menu {
		display: block;
		width: 100px;
		padding: 2px 5px;
		background: #8F8F8F;		
		color: #F0F0F0;
		text-align: center;
		font-family: Sans-Sherif;
		font-size: 0.9em;
		font-weight: 900;
		text-decoration: none;
	}	
	</style><title>Index</title></head><body style="font-family: arial,verdana">
	$(bookmf)
EOF

if test -s bookmarks.html; then
	echo "<p class=\"Menu\">Bookmarks</p>"
	cat bookmarks.html
	echo "<button type=button onClick=\"rmbookmark()\">Remove Current</button>"
	echo "<button type=button onClick=\"rmall()\">Remove All</button>"
	echo "<p class=\"Menu\">Menu</p>"
fi

cat<<EOF
	<a href="/cgi-bin/logout.cgi" target="content">Logout</a><br>
	<a href="/cgi-bin/status.cgi" target="content">Status</a><br>
EOF

for i in Setup Disk Services Packages System; do
	echo "<a href=\"/cgi-bin/index.cgi?pg=$i\">$i</a><br>"
	IFS=" "
	if test "$i" = "$pg"; then
		extra=$(cat $i*.men)
		echo $extra | while read entry url; do
			echo "&emsp;<a href=\"/cgi-bin/$url\" target=\"content\">$entry</a><br>"
		done
	fi
done

echo "<button type=button onClick=\"addbookmark()\">Bookmark Current</button></body></html>"