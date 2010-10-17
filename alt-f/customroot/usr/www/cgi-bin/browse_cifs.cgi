#!/bin/sh

. common.sh
check_cookie

html_header
echo "<h2><center>Samba Browse</center></h2>"

if test -n "$QUERY_STRING"; then		
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')
else
	echo "<h3>No arguments given.</h3></body></html>"
	exit 0
fi

cat <<-EOF
	<script type="text/javascript">
		function ret_val(id1, host, id2, dir) {
			window.opener.document.getElementById(id1).value = host;
			window.opener.document.getElementById(id2).value = dir;
			window.close();
		}
	</script>
EOF

wait_count_start "Browsing the network for Samba servers, it takes 10 seconds"

if false; then

F1=domain
F2=host
F3=//host/share
F4=comment

domain: F1 not empty
host: F2 not empty
share: F2 empty && F3 not empty
fi

echo "<table><tr><th>Share</th><th>Comment</th></tr>"

smbtree -N | tr '\t' ':' | awk -F : '{
	if ($2 != "")
		printf "<tr><td><br></td></tr><tr><td><strong>%s</strong></td><td>%s</td></tr>\n", $2, $4
	if ($2 == "" && $3 != "") {
		if (index($3,"$"))
			next
		split($3, a,"\\");
		gsub(" *$","",a[3]); # not workink in js gsub(" ","\\ ",a[3]); 
		gsub(" *$","",a[4]); # not workink in js gsub(" ","\\ ",a[4]);
		rhost=a[3];  rdir=a[4];
		printf "<tr><td><a href=\"\" onclick=\"ret_val(%c'$id1'%c, %c%s%c, %c'$id2'%c, %c%s%c)\">%s</a></td><td>%s</td></tr>\n", \
		047, 047, 047, rhost, 047, 047, 047, 047, rdir, 047, $3, $4
	} 
}'

wait_count_stop

echo "</table><br><form><input type=submit onclick=\"window.close()\" value=Cancel></form></body></html>"

exit 0
