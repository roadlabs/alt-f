#!/bin/sh

. common.sh
check_cookie
write_header "Disk Partitioning"

s="<strong>"
es="</strong>"
c="<center>"
ec="</center>"

disks=$(ls /dev/sd? 2> /dev/null)

if test -z "$disks"; then
	echo "<br> $s No disks found $es <br>"
	echo "</body></html>"
	exit 1
fi

cat<<-EOF
	<script type="text/javascript">
	function ask(msg) {
		return confirm(msg);
        }
	function keeppart(ipart) {
		st = document.getElementById("keep_" + ipart).checked;
		document.getElementById("cap_" + ipart).disabled = st;
		document.getElementById("type_" + ipart).disabled = st;
		raidsel(ipart);
	}
	function raidsel(ipart) {
		dis = document.getElementById("type_" + ipart).disabled;
		type = document.getElementById("type_" + ipart).selectedIndex;

		stat = false;
		if (type != 1) // 0-empty 1-raid, 2-swap, 3-linux, 4-vfat, 5-ntfs
			stat = true;

		document.getElementById("raid_" + ipart).disabled = stat || dis;
		raidtype(ipart)

	}
	function raidtype(ipart) {
		dis = document.getElementById("raid_" + ipart).disabled;
		document.getElementById("pair1_" + ipart).disabled = dis;
		document.getElementById("pair2_" + ipart).disabled = dis;
		if (dis == true)
			return;

		type = document.getElementById("raid_" + ipart).selectedIndex;

		stat = false;
		if (type == 0)
			stat = true;
		document.getElementById("pair1_" + ipart).disabled = stat;

		stat = false;
		if (type < 3) // 0-none, 1-jbd, 2-raid0, 3-raid1, 4-raid5
			stat = true;
		document.getElementById("pair2_" + ipart).disabled = stat;
	}
	function updatefree(dcap, dsk, part) {
		free = dcap;
		for (i=1; i<=4; i++)
			free -= document.getElementById("cap_" + dsk + i).value*1000;
		document.getElementById("free_id").value = free/1000;

		if (document.getElementById("cap_" + part).value == 0)
			document.getElementById("type_" + part).selectedIndex = 0;
	}
	function reopen(dsk) {
		url=window.location + "?disk=" + dsk;
		window.location.assign(url)
	}

	</script>
	<form action="/cgi-bin/diskpart_proc.cgi" method="post">
EOF

if test -n "$QUERY_STRING"; then
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')
	dsk="/dev/$(httpd -d "$disk")"
else
	dsk="/dev/sda"
fi

ntfsopt="disabled"
if test -f /usr/sbin/mkntfs; then
	ntfsopt=""
fi

pairs="$(fdisk -l | awk 'substr($1,1,8) != "'$dsk'" && ($5 == "da" || $5 == "fd") {
		nm = substr($1, 6); 
		printf ("<option value=%s>%s %.0fGB</option>", nm, nm, $4/1048576)}')"

cat<<-EOF
	<fieldset>
	<legend><strong>Select the disk you want to partition</strong></legend>
	<table><tr>
	<th>Partition</th>
	<th>Bay</th>
	<th>Device</th>
	<th>Capacity</th>
	<th>Model</th>
	</tr>
EOF

ndisks=0
for i in $disks; do
	disk=$(basename $i)

	mod=$(cat /sys/block/$disk/device/model)
	cap=$(awk '{printf "%.1f", $1*512/1e9}' /sys/block/$disk/size)
	bay=$(awk '/'$disk'/{print toupper($1)}' /etc/bay)

	chkd=""	
	if test "$i" = "$dsk"; then chkd="checked"; fi

	cat<<-EOF
		<tr>
		<td><input type=radio $chkd name=disk value=$disk onchange="reopen('$disk')"></td>
		<td>$bay</td>
		<td align=center>$disk</td>
		<td align=right>$cap GB</td>
		<td>$mod</td>
		</tr>
	EOF
	ndisks=$((ndisks + 1))
done
echo "</table></fieldset><br>"	

ddsk=$(basename $dsk)
rawcap=$(expr $(sfdisk -s $dsk) \* 1024 / 1000000)

mod=$(cat /sys/block/$ddsk/device/model)
diskcap=$(awk '{printf "%.1f", $1*512/1e9}' /sys/block/$ddsk/size)
bay=$(awk '/'$ddsk'/{print toupper($1)}' /etc/bay)

cat<<-EOF
	<fieldset>
	<legend><strong>Partition $bay disk, $diskcap GB, $mod </strong></legend>
	<table>
	<tr align=center>
	<th> Keep </th>
	<th> Part. </th>
	<th> Type </th>
	<th> Size (GB) </th>
	<th> Type </th>
	<th> RAID </th>
	<th> Pair with </th>
	<th> Pair/Spare </th>
	</tr>
EOF

fout=$(sfdisk -l $dsk | tr '*' ' ') # *: the boot flag...

if $(echo $fout | grep -q "No partitions found"); then
	fout="${dsk}1          0       -       0          0    0  Empty
${dsk}2          0       -       0          0    0  Empty
${dsk}3          0       -       0          0    0  Empty
${dsk}4          0       -       0          0    0  Empty"
fi

used=0
for pl in 1 2 3 4; do
	part=${dsk}$pl
	ppart=$(basename $part)
	id=""; type="";cap=""
	eval $(echo "$fout" | awk '
		/'$ppart'/{printf "id=\"%s\" type=\"%s\"; cap=%.1f; rcap=%d", \
		$6, substr($0, index($0,$7)), $5*1024/1e9, $5}')

	used=$((used + rcap))

	emptys=""; swaps=""; linuxs=""; raids=""; vfats=""; ntfss=""
	nones=""; raid0s=""; raid1s=""; raid5s=""; jbds=""; rlevel=""
	xpair1=""; xpair2=""
	case $id in
		0) emptys="selected" ;;
		82) swaps="selected" ;;
		83) linuxs="selected" ;;
		fd|da) raids="selected"
			eval $(mdadm --examine $part 2> /dev/null | awk -v part=$ppart '
				BEGIN { excl = part }
				/Raid Level/ { printf "rlevel=%s; ", $4 }
				/this/ { getline; while (getline) {
					if (substr($NF, 1,5) == "/dev/") { 
						dev = substr($NF, 6, 4);
						if (dev != excl)
							devs[i++] = dev }}}
				END {printf "p1=%s; p2=%s", devs[0], devs[1]}')

			case "$rlevel" in
				raid0) raid0s="selected" ;;
				raid1) raid1s="selected" ;;
				raid5) raid5s="selected" ;;
				jbd) jbds="selected" ;;
				*) nones="selected" ;;
			esac
			if test -n "$p1"; then
				xpair1="<option selected value=$p1>$p1 *</option>"
			fi
			if test -n "$p2"; then
				xpair2="<option selected value=$p2>$p2 *</option>"
			fi
			;;
		b|c) vfats="selected" ;;
		7) ntfss="selected" ;;
	esac

	cat<<-EOF
	<tr>
	<td align=center><input type=checkbox checked id=keep_$ppart name=keep_$ppart value=yes 
		onclick="keeppart('$ppart')"</td>
	<td>$ppart</td>
	<td>$type</td>
	<td><input type=text disabled size=6 id=cap_$ppart name=cap_$ppart 
		value=$cap onchange="updatefree('$rawcap', '$ddsk', '$ppart')"></td>
	<td><select disabled id=type_$ppart name=type_$ppart 
		onclick="raidsel('$ppart')">
	<option $emptys>empty</option>
	<option $raids>RAID</option>
	<option $swaps>swap</option>
	<option $linuxs>linux</option>
	<option $vfats>vfat</option>
	<option $ntfss $ntfsopt>ntfs</option>
	</select></td>

	<td><select disabled id=raid_$ppart name=raid_$ppart 
		onclick="raidtype('$ppart')">
	<option $nones>none</option>
	<option $jbds>JBD</option>
	<option $raid0s>raid0</option>
	<option $raid1s>raid1</option>
	<option $raid5s>raid5</option>
	</select></td>

	<td><select disabled id=pair1_$ppart name=pair1_$ppart>
	<option>missing</option>
	$pairs
	$xpair1
	</select></td>

	<td><select disabled id=pair2_$ppart name=pair2_$ppart>
	<option>missing</option>
	$pairs
	$xpair2
	</select></td>

	</tr>
	EOF

done 

free="$(expr $rawcap - $used \* 1024 / 1000000)"
free=$(awk 'BEGIN {printf "%.3f", ('$rawcap' - '$used' * 1024/1e6)/1000}')

cat<<-EOF
	<tr><td colspan=2></td>
	<td align=right>Free</td>
	<td><input type=text readonly id="free_id" size=6 value="$free"></td>
	</tr>
	<tr><td align=center colspan=2><input type=submit name=$ddsk value=Partition
		onclick="return ask('Partitioning the $diskcap GB $bay disk can make all its data inacessible.\n\nContinue?')"></td>
	</tr>
	</table></fieldset><br>
	</form></body></html>
EOF

# wizard, not yet

exit 0

nodisk="checked"; no2disk=""; no3disk=""
case "$ndisks" in
	0)	nodisk=disabled ;;
	1)	no2disk=disabled; no3disk=disabled; ;;
	2)	no3disk=disabled ;;
	*)	;;	
esac

cat<<-EOF
	<fieldset>
	<legend><strong>Please advise, I want...</strong></legend>
	<table>
	<tr><td align=center>
		<input type=radio $nodisk name=suggest value=standard></td>
		<td>One big standard partition per disk, easy management</td></tr>
	<tr><td align=center>
		<input type=radio $no2disk name=suggest value=jbd></td>
		<td>Merge the two disks in one big partition, low data security (JDB)</td></tr>
	<tr><td align=center>
		<input type=radio $no2disk name=suggest value=raid0></td>
		<td>Maximum performance on both disks and low data security (raid0)</td></tr>
	<tr><td align=center>
		<input type=radio $no2disk name=suggest value=raid1></td>
		<td>Duplicate everything on both disks (raid1)</td></tr>
	<tr><td align=center>
		<input type=radio $no3disk $threedisks name=suggest value=raid5></td>
		<td>Performance and security, with two disks plus an external USB disk (raid5)</td></tr>
	<tr><td align=center>
		<input type=submit name=advise value=Advise onclick="alert('Not yet')"></td></tr>
	</table></fieldset>
	</form></body></html>
EOF
