#!/usr/bin/perl
####################################################################################################
#                                       Oracle Archives
#
#       Author: Bernardo Vale
#       Date: 06/03/2014
#       Version: 1.0
#       Contact:  bernardo.vale@lb2.com.br or bernardosilveiravale@gmail.com
#
#       Propertie of LB2 Consultoria e Tecnologia LTDA
####################################################################################################
use strict;
require 5.6.0;
use lib qw(/usr/local/nagios/libexec);
use utils qw(%ERRORS $TIMEOUT &print_revision &support &usage);

my $host = $ARGV[1];
my $port = $ARGV[2];
my $sid  = $ARGV[3];
my $user  = $ARGV[4];
my $pass  = $ARGV[5];
my $archives = $ARGV[6];
my $archives_day = $ARGV[7];
my $perf_data = "";
my $message = "";
#Essa variavel e para eu poder concatenar e mostrar todos checagens que deu warning antes de sair
my $die = 0;
sub trim($);
my @result;
my %ERRORS=('OK'=>0,'WARNING'=>1,'CRITICAL'=>2);
#Definição das query. Pode ser outro comparador alem do > <
my @param_array = (
    [$archives,"<","Current Archives/hr",'select count(*) from v\$log_history
			where trunc(sysdate,\'DD\') = trunc(first_time,\'DD\')
			and trunc(sysdate,\'HH24\') = trunc(first_time,\'HH24\');'],
    [$archives_day,"<","Total Archives/day",'select count(*) from v\$log_history
			where TO_CHAR(first_time,\'MM/DD/YYYY\') = TO_CHAR(SYSDATE,\'MM/DD/YYYY\');']
               );
my @results;

sub array_rows {
    my ($array_rows) = @_;

    my $rows = @$array_rows;
    return $rows;
       }

sub trim($)
{
        my $string = shift;
        $string =~ s/^\s+//;
        $string =~ s/\s+$//;
        return $string;
}


sub logon {
open (SQL,"sqlplus -s $user/mismatch@\\(DESCRIPTION=\\(ADDRESS=\\(PROTOCOL=TCP\\)\\(Host=$host\\)\\(Port=$port\\)\\)\\(CONNECT_DATA=\\(SID=$sid\\)\\)\\)</dev/null
|") or die;
  while ( my $res = <SQL> )
             {
           if ($res =~ /^(ORA-\d{5})/) {return $1;}
             }
}

if (logon() eq "ORA-01017"){


 my $i = 0;
 for ($i; $i<array_rows(\@param_array); $i++){
        #$perf_data = $perf_data . $param_array[$i][2] . " "; #Nome da checagem
        #print "$param_array[$i][0] -- $param_array[$i][1] -- $param_array[$i][2] -- $param_array[$i][3]\n";

open (SQL,"sqlplus -s $user/$pass@\\(DESCRIPTION=\\(ADDRESS=\\(PROTOCOL=TCP\\)\\(Host=$host\\)\\(Port=$port\\)\\)\\(CONNECT_DATA=\\(SID=$sid\\)\\)\\) << EOF
set pagesize 0
set numformat 9999.999
$param_array[$i][3]
EOF |") or die;
  while ( my $res = <SQL> )
             {
   #print trim($res)."\n";
   if ( $res =~/^\s*\S+/ ) {
        #print $res;
        $perf_data = $perf_data . $param_array[$i][2] . "=" . trim($res) . ";" . $param_array[$i][0] . " ";
        #$i = $i +1;
        #print $perf_data;
        push(@results,trim($res));
        }
             }
  }
  for ($i=0;$i<@results;$i++) {
        #Checa a condicão booleana X > Y? Caso falhe ja da um warning no garoto
        my $answer = eval($results[$i] . $param_array[$i][1] . $param_array[$i][0]);
        if ($answer != 1){
                #Aciona a flag sair com warning
                $die = 1;
                # Concatena o cara que não passou na checagem!
                $message = $message . "VERIFICAR A QUANTIDADE DE ARCHIVES NO BANCO $sid Condição: $archives > $results[0] e $archives_day > $results[1] !!!\n"
        }
   }
   if ($die==0){
        print "Geração de archives no banco $sid esta OK Condição: $archives > $results[0] e $archives_day > $results[1]" . " | " . $perf_data;
        exit $ERRORS{"OK"};
   }else{
                print $message . "| $perf_data";
                exit $ERRORS{"WARNING"};
        }

} else {print "A base $sid nao conecta!!! "; exit $ERRORS{"CRITICAL"};}