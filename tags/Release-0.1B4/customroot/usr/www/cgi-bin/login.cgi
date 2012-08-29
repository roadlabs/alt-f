#!/bin/sh

. common.sh
write_header "Alt-F Login"

SECR=/etc/web-secret

cat<<-EOF
    <center>
	<form action="/cgi-bin/login_proc.cgi" method="post">
    <table>
	<tr><td>Password:</td>
		<td><input type="password" autocomplete="off" name="passwd"></td>
EOF

if ! test -e $SECR; then
	cat<<-EOF
		</tr>
		<tr><td>Again:</td>
			<td><input type="password" autocomplete="off" name="passwd_again"></td>
	EOF
fi

cat<<-EOF
		<td><input type="submit" value="Submit"></td>
	</tr>
	</table>
	<input type="hidden" name=from_url value="$(basename $REQUEST_URI)">
	</form></center>
	</body></html>
EOF