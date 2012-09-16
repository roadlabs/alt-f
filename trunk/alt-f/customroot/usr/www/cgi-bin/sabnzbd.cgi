#!/bin/sh

. common.sh
check_cookie
read_args

write_header "SABnzbd Setup"

CONFF=/etc/sabnzbd/sabnzbd.conf

maindir=$(sed -n 's|^dirscan_dir *= *\(.*\)|\1|p' $CONFF)

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
			start_dir = document.getElementById(input_id).value;
			if (start_dir == "")
				start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
	</script>

	<form name=sabnzbd action=sabnzbd_proc.cgi method="post" >
	<table>
	<tr><td>SABnzbd Folder</td>
	<td><input type=text size=32 id="conf_dir" name="conf_dir" value="$(httpd -e "$maindir")"></td>
	<td><input type=button onclick="browse_dir_popup('conf_dir')" value=Browse></td>
	</tr>
	<tr><td></td><td>
	<input type=submit name=submit value=Submit> $(back_button)
	<input type="submit" name=webPage value=WebPage>
	</td></tr></table></form></body></html>
EOF