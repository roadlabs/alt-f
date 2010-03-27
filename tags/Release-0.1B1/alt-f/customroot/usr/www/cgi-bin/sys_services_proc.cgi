#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

start_stop() {
    local serv act
    serv=$1
    act=$2

    sscript=/etc/init.d/*$serv
	if test -n "$sscript"; then    
		if test "$act" = "enable"; then
			chmod +x $sscript
			$sscript start >/dev/null 2>&1
		elif test "$act" = "disable"; then
			$sscript stop >/dev/null 2>&1
			chmod -x $sscript
		elif test "$act" = "start"; then
			sh $sscript start >/dev/null 2>&1
		elif test "$act" = "stop"; then
			sh $sscript stop >/dev/null 2>&1
		fi
    fi
}

. common.sh
read_args
check_cookie

#debug

srv="cron at syslog smart ffp"
idx=1

for i in $srv; do
	serv=$(eval echo \$$i)

	if test -z "$serv" -a -x /etc/init.d/S??$i; then
		start_stop $i disable
	elif test "$serv" = "enable" -a ! -x /etc/init.d/S??$i; then
		start_stop $i enable
	elif test "$serv" = "StartNow"; then
		start_stop $i start
	elif test "$serv" = "StopNow"; then
		start_stop $i stop
	fi

	if test "$serv" = "Configure"; then
            gotopage /cgi-bin/${i}.cgi
	fi

	idx=$((idx+1))
done

#debug

gotopage /cgi-bin/sys_services.cgi
