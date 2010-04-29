#!/bin/sh
. common.sh

check_cookie
write_header "ipkg Package Manager"

#debug

s="<strong>"
es="</strong>"

if ! test -f /Alt-F/usr/bin/ipkg-cl; then

	disks=$(ls /dev/sd?) >/dev/null 2>&1

	if test -z "$disks"; then
		echo "<br> $s No disks found! $es <br>"
		echo "</body></html>"
		exit 1
	fi

	cat<<-EOF
		<h4>No ipkg instalation found, install ipkg in:</h4>
		<form action="/cgi-bin/packages_ipkg_proc.cgi" method=post>
	EOF
	select_part
	echo "</select><input type=submit name=install value=Install>
	</form></body></html>"

else

ipkg-cl -V0 info | awk '
	/Package:/{i++; nm=$2; pkg[i] = nm} # this relies on Package being the first field 
	/Version:/{ver[i] = $2} 
	/Source:/{url[i] = $2} 
	/Description:/{des[i] = substr($0, index($0,$2))} 
	/Status:/{if ($4 == "installed") inst[nm] = i; else uinst[nm] = i} 
	END {
		print "<form action=\"/cgi-bin/packages_ipkg_proc.cgi\" method=post> \
		<fieldset><legend><strong> Installed Packages </strong></legend> \
		<table><tr> \
			<th>Name</th><th>Version</th><th></th><th></th><th>Description</th> \
		</tr>"

		for (nm in inst) {
			if (nm in uinst) { # info in inst is incomplete in this case
				i=uinst[nm]; v=ver[inst[nm]]; update=1;
				upd=sprintf("<td><input type=submit name=%s value=Update></td>", nm);
				delete uinst[nm];
			} else {
				i=inst[nm]; v=ver[i];
				upd="<td></td>";
			}
			printf "<tr><td><a href=\"%s\">%s</a></td><td>%s</td>",
				url[i], nm, v;
			printf "<td><input type=submit name=%s value=Remove></td>", nm;
			print upd;
			printf "<td>%s</td></tr>\n\n", des[i];
		}
	
		if (update == 1)
			print "<tr><td></td><td></td><td></td> \
				<td><input type=submit name=updateall value=UpdateAll></td></tr>"

		print "</table></fieldset> \
			<br><fieldset><legend><strong> Available Packages </strong></legend> \
			<table><tr> \
			<th>Name</th><th>Version</th> \
			<th></th><th>Description</th></tr>"

		for (nm in uinst) {
			i=uinst[nm];
			printf "<tr><td><a href=\"%s\">%s</a></td><td>%s</td>",
				url[i], nm, ver[i];
			printf "<td><input type=submit name=%s value=Install></td>", nm;
			printf "<td>%s</td></tr>\n\n", des[i];
		}
		print "</table></fieldset><br> \
		<input type=submit name=updatelist value=UpdateList> \
		<input type=submit name=configfeed value=ConfigureFeed> \
		</form>"
	}'

fi
