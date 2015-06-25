#!/bin/bash
# -------------------------------------------------------------
#                 check_cpu, usando o comando "procinfo"
#                   criado para usar no SUSE 10
#
#       Autor: Eduardo Lopes de Melo
#       Data Inicio:  01/05/2015
#       Data Release: 05/05/2015
#       email: eduardo.melo@lb2.com.br
#       Versão: v1.0
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------
while [ $# -gt 0 ]; do
        case "$1" in
                -w | --warning)
                        shift
                        WARNING_THRESHOLD=$1
                ;;
                -c | --critical)
                        shift
                        CRITICAL_THRESHOLD=$1
                ;;
                *)  echo "Unknown argument: $1"
                    echo "  -w  <number> : Warning level in % "
                    echo "  -c  <number> : Critical level in % "
                        exit
                ;;
        esac
   shift
done

info=`procinfo | grep -r "user\|system\|IOwait\|idle" | cut -d% -f1 | awk '{print $NF}' | cut -d. -f1`
value=( $info )

user=${value[0]}
system=${value[1]}
IOwait=${value[2]}
idle=${value[3]}
used=`expr 100 - ${value[3]}`


if [[ $used -gt $CRITICAL_THRESHOLD ]]; then
        msg="CRITICAL"
        status=2
else if [[ $used -gt $WARNING_THRESHOLD ]]; then
        msg="WARNING"
        status=1
     else
        msg="OK"
        status=0
     fi
fi

echo "CPU $msg : idle $idle% | User=$user% System=$system% IOwait=$IOwait% Usage=$used% idle=$idle%"

exit $status