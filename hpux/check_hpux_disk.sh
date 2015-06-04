#!/bin/ksh
#
# Filename - check_diskuse
#
# Program: Checks the diskuse on your hp-ux box and reports the status
# License : GPL or whatever you want it to be... seriously I dont see the point in having any copyright on scripts...
# 2007 Marius van Vuuren (boomroker@gmail.com)
#
# Updated on 04/05/2015 By Todd Litteken
#
# Added -c and -w to set warning and critical alert points.
# Removed "cuitie" responces and made it more profecional.
#
# Updated on 03/06/2015 By Bernardo Vale
#
# Added performance Data to show disk growth
#
# check_diskuse ,v 1.2 03/06/2015
#
# Description :
#
#  This plugin checks if the disk usage is below the warning and critical levels.
#  You might need to edit the PERCENTUSED awk print variable depending on your OS.
#
# Usage :
#
#  check_diskuse -s filesystem :: example: check_diskuse -s home  
#
# Example :
#
#  To check if home is good on space
# check_diskuse -s home
# > OK - filesystem is sweet : Percent Used 70%
#
# HP-UX - Should be universal but I wrote this for my HP boxes I have to look after
#

help_usage() {
    echo "Usage:"
    echo " $0 -s filesystem (not mountpoint)"
        echo " $0 (-c critical)"
        echo " $0 (-w warning)"
        echo " $0 (-v | --version)"
        echo " $0 (-h | --help)"
}

help_version() {
    echo "check_diskuse (nagios-plugins) 1.0"
    echo "The nagios plugins comes with ABSOLUTELY NO WARRANTY. You may redistribute"
    echo "copies of the plugins under the terms of the GNU General Public License."
	echo "2007 Marius van Vuuren - boomroker@gmail.com"
    echo "If your hiring call me :-)"
}

myself=$0

if [ "$1" = "-h" -o "$1" = "--help" ]
then
	help_version
	echo ""
	echo "This plugin will check if diskspace is ok."
	echo ""
	help_usage
	echo ""
	echo "Required Arguments:"
    	echo " -s, --stream STRING"
    	echo "    filesystem as in /etc/fstab"
	echo ""
	exit 3
fi

if [ "$1" = "-v" -o "$1" = "--version" ]
then
	help_version
    	exit 3
fi

if [ `echo $@|tr "=" " "|wc -w` -lt 2 ]
then
	echo "Bad arguments number (need two)!"
	help_usage
	exit 3
fi

stream=""
wt=""
ct=""
crit=""

# Test of the command lines arguments
while test $# -gt 0
do

	case "$1" in
		-s|--stream)
			if [ -n "$stream" ]
			then
			 echo "Only one --stream argument is useful..."
                         help_usage
                         exit 3
			fi
			shift
			stream="`echo $1|tr \",\" \"|\"`"
		;;
		-c)
			shift
			CRITICAL="`echo $1`"
		;;
		-w)
			shift
			WARNING="`echo $1`"
		;;
		*)
			echo "Unknown argument $1"
			help_usage
			exit 3
		;;
		esac
		shift
		done

# bdf construction
FSTAB="/etc/fstab"

FILESYSTEM=$(cat $FSTAB | grep $stream | awk ' { print $1 } ' | head -1)
PERCENTUSED=$(bdf $FILESYSTEM| awk '{if (NF==1) {line=$0;getline;sub(" *"," ");print line$0} else {print}}' | tail -1 | sed 's/'%'//' | awk ' { print $5 } ')

if [ "$PERCENTUSED" -gt "$WARNING" ] && [ "$PERCENTUSED" -lt "$CRITICAL" ]
then
	crit=1
elif [ "$PERCENTUSED" -ge "$CRITICAL" ]
then
	crit=2
else
	crit=0
fi

# Finally Inform Nagios of what we found...
if [ $crit -eq 1 ]
then
	echo "WARNING -  Filesystem $FILESYSTEM is $PERCENTUSED% full | DISK_USAGE=$PERCENTUSED"
	exit 1
elif [ $crit -eq 2 ]
then
	echo "CRITICAL - Filesystem $FILESYSTEM is $PERCENTUSED% full | DISK_USAGE=$PERCENTUSED"
	exit 2
else
	echo "OK - Filesystem $FILESYSTEM is $PERCENTUSED% full | DISK_USAGE=$PERCENTUSED"
	exit 0
fi

# Hey what are we doing here ???
exit 3