#!/bin/bash
# -------------------------------------------------------------
#      Check_cpu - usando o comando "top" do linux. Criado para o SUSE 10
#                   ou qualquer outra distro.
#                Este foi criado para suprir a deficiencia do
#               comando "procinfo", onde a saida do usage retornava
#
#       Autor: Eduardo Lopes de Melo
#       Data Inicio:  01/05/2015
#       Data Release: 05/05/2015
#       email: eduardo.melo@lb2.com.br
#       Versão: v1.0
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------

#!/bin/bash
#     ---%
#
###########################################################################################################
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

info=`top -bn1 | grep "Cpu(s)" | sed 's/[a-z]/ /g' | sed 's/C  ( ):  //g' | sed 's/  ,  / /g' | sed 's/  , / /g' | sed 's/%//g' | sed 's/ /\n/g' | cut -d. -f1`
value=( $info )

user=${value[0]}
system=${value[1]}
idle=${value[3]}
IOwait=${value[4]}
used=`expr 100 - $idle`

if [[ $used -ge $CRITICAL_THRESHOLD ]]; then
        msg="CRITICAL"
        status=2
else if [[ $used -ge $WARNING_THRESHOLD ]]; then
        msg="WARNING"
        status=1
     else
        msg="OK"
        status=0
     fi
fi

echo "CPU $msg : idle $idle% | User=$user% System=$system% IOwait=$IOwait% Usage=$used% idle=$idle%"

exit $status