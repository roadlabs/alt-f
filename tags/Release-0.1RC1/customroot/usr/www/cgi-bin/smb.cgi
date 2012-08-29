#!/bin/sh

. common.sh
check_cookie
write_header "Samba Setup"

CONF_SMB=/etc/samba/smb.conf
CONF_FST=/etc/fstab

# fstab_rows ln cnt
fstab_row() {
	local ln cnt hostdir mdir rhost rdir opts nfs
	ln=$1; cnt=$2

	eval $(echo $ln | awk '$3 == "cifs" {
		printf "hostdir=\"%s\"; mdir=\"%s\"; opts=%s", $1, $2, $4}')

	eval $(echo $hostdir | awk -F"/" '{
		printf "rhost=\"%s\"; rdir=\"%s\"", $3, substr($0, index($0,$4))}')

	rdir="$(path_unescape $rdir)"
	mdir="$(path_unescape $mdir)"

	cmtd=${hostdir%%[!#]*}	# get possible comment char
	if test -n "$cmtd"; then dis_chk=checked; else dis_chk=""; fi

	mntfld="<td></td>"
	if test -n "$mdir"; then
		op="Mount"
		if mount -t cifs | grep -q "$mdir"; then
			op="unMount"
		fi
		mntfld="<td><input type=submit value=\"$op\" name=\"$mdir\" onclick=\"return check_dis('$dis_chk','$op')\"></td>"
	fi

	cat<<-EOF
		<tr>
		<td align=center><input type=checkbox $dis_chk id="fstab_en_$cnt" name="fstab_en_$cnt" value="#" onclick="return check_mount('$op','fstab_en_$cnt')"></td>
		$mntfld
		<td><input type=text size=10 id=rhost_$cnt name=rhost_$cnt value="$rhost"></td>
		<td><input type=text size=12 id=rdir_$cnt name=rdir_$cnt value="$rdir"></td>
		<td><input type=button value=Browse onclick="browse_cifs_popup('rhost_$cnt', 'rdir_$cnt')"></td>
		<td><input type=text size=12 id=mdir_$cnt name=mdir_$cnt value="$mdir"></td>
		<td><input type=button value=Browse onclick="browse_dir_popup('mdir_$cnt')"></td>
		<td><input type=text size=20 id=mntopts_$cnt name=mopts_$cnt value="$opts" onclick="def_opts('mntopts_$cnt')"></td>
		</tr>
	EOF
}

cat<<EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
		    start_dir = document.getElementById(input_id).value;
		    if (start_dir == "")
		    	start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function browse_cifs_popup(host_id, dir_id) {
			window.open("browse_cifs.cgi?id1=" + host_id + "?id2=" + dir_id, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
        }
		function def_opts(id) {
			var opts = document.getElementById(id);
			if (opts.value != "")
				return;
			opts.value = "uid=root,gid=users,credentials=/etc/samba/credentials.root,rw,iocharset=utf8,nounix,noserverino"
		}
		function check_mount(op, id) {
			if (op == "unMount" && document.getElementById(id).checked == true) {
				alert("To disable an entry you must first unmount it.")
				return false
			}
			return true
		}
		function check_dis(sel, op) {
			if (sel == "checked" && op == "Mount") {
				alert("To mount an entry you must first enable it and Submit")
				return false
			}
			return true
		}
	</script>
	<form id=smbf name=smbf action=smb_proc.cgi method="post">
	<fieldset>
	<legend><strong>Directories to export to other hosts</strong></legend>
	<table>
	<tr>
		<th>Disable</th>
		<th>Directory</th>
		<th>Browse</th>
		<th>Share Name</th>
		<th>Comment</th>
		<th align=center>Browseable</th>
		<th>Public</th>
		<th>Read Only</th>
	</tr>
EOF

#awk -F = '/#!#/ {
awk -F = ' {
		mark_found = 1
	}
	/\[.*\]/ {
		if (mark_found == 0)
			next

		parse( pshare($0), $0)
		delete opts
	}
	END {
		for (i=cnt+1; i<cnt+4; i++)
			spit(i, opts)
		printf "</table><input type=hidden name=smb_cnt value=\"%d\">", i
	}

function pshare(line) {
	i = index(line, "[") + 1
	return substr(line, i, index(line, "]") - i)
}

function spit(cnt, opts) {
	
	rdir = public_chk = rdonly_chk = dis_chk = browse_chk = ""

	if (opts["path"] != "") {
		sprintf("readlink -f \"%s\" ", opts["path"]) | getline rdir
		if (rdir == "") {
			rdir = opts["path"]
			opts["available"] = "no"
		}
		browse_chk = "checked"
		if (opts["browseable"] == "no")
			browse_chk = ""		
		if (opts["public"] == "yes")
			public_chk = "checked"
		if (opts["read only"] == "yes")
			rdonly_chk = "checked"
		if (opts["available"] == "no")
			dis_chk = "checked"
	}

	printf "<tr><td align=center><input type=checkbox %s name=avail_%d value=no></td>", dis_chk, cnt
	printf "<td><input type=text id=ldir_%d name=ldir_%d value=\"%s\"></td>\n", cnt, cnt, rdir
	printf "<td><input type=button  onclick=\"browse_dir_popup(%cldir_%d%c)\" value=Browse></td>\n", 047, cnt, 047
	printf "<td><input type=text size=8 name=shname_%d value=\"%s\"></td>\n", cnt, opts["share_name"]
	printf "<td><input type=text name=cmt_%d value=\"%s\"></td>\n", cnt, opts["comment"]
	printf "<td align=center><input %s type=checkbox name=browse_%d value=yes></td>\n", browse_chk, cnt
	printf "<td align=center><input %s type=checkbox name=public_%d value=yes></td>\n", public_chk, cnt
	printf "<td align=center><input %s type=checkbox name=rdonly_%d value=yes></td>\n", rdonly_chk, cnt 
	print "</tr>\n"
}

function parse(share_name, line) {
	if (tolower(share_name) == "global" || tolower(share_name) == "printers")
		next

	cnt++
	delete opts
	opts["share_name"] = share_name 
	while (st = getline) {
		fc = substr($0,1,1)
		if (fc == "#" || fc == ";")
			continue
		if (fc == "[")
			break

		gsub("^( |\t)*|( |\t)*$","", $1)
		gsub("^( |\t)*|( |\t)*$","", $2)
		opts[$1] = $2
	}

	spit(cnt, opts)

	if (st == 0)
		return

	parse(pshare($0), $0)
}' $CONF_SMB

cat<<-EOF
	</fieldset><br>

	<fieldset>
	<legend><strong>Directories to import from other hosts</strong></legend>
	<table>
	<tr align=center>
	<th>Disable</th>
	<th></th>
	<th>Host</th>
	<th>Directory</th>
	<th>Discover</th>
	<th>Local dir</th>
	<th>Search</th>
	<th>Mount Options</th>
	</tr>
EOF

cnt=1
while read -r ln; do
	if echo "$ln" | grep -q cifs; then
		fstab_row "$ln" $cnt
		cnt=$((cnt+1))
	fi
done < $CONF_FST

i=$cnt
for i in $(seq $cnt $((cnt+2))); do
	fstab_row "" $i	# ln cnt
done

cat<<EOF
	</table><input type=hidden name=import_cnt value=$i>
	</fieldset><br>
	$(back_button)<input type=submit name=submit value="Submit">
	<input type=submit name=submit value="Advanced">
	</form></body></html>
EOF
