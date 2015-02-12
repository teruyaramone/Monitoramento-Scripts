#!/usr/bin/python
# coding=utf-8
import sys

__author__ = 'Bernardo Vale'
__enterprise__ = 'LB2 Consultoria e Tecnologia LTDA'

import argparse
import cx_Oracle


def parse_args():
    """
    Método de analise dos argumentos do software.
    Qualquer novo argumento deve ser configurado aqui
    :return: Resultado da analise, contendo todas as variáveis resultantes
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--sid', required=True, action='store',
                        dest='sid',
                        help='Service name do banco de produção.')
    parser.add_argument('--user', required=True, action='store',
                        dest='user',
                        help='Usuário do banco: sys,system etc..')
    parser.add_argument('--pwd', required=True, action='store',
                        dest='pwd',
                        help='Senha do usuário especificado!')

    parser.add_argument('--host', required=True, action='store',
                        dest='host',
                        help='IP do banco!')
    p = parser.parse_args()
    return p

def estabConnection(user, pwd, sid, host, is_sysdba):
    """
        Tenta conectar no Oracle com as credenciais
        :param user: Usuário do banco
        :param senha: Senha do banco
        :param sid: service-name do banco
        :return: Uma conexão ativa com o banco
        """
    try:
        if is_sysdba:
            conn = cx_Oracle.connect(user + '/' + pwd + '@' + host + '/' + sid, mode=cx_Oracle.SYSDBA)
        else:
            conn = cx_Oracle.connect(user + '/' + pwd + '@' + host + '/' + sid)
    except:
        print "CRITICAL - Falha na conexao com a base, cheque os parametros!"
        sys.exit(2)
    return conn

def calc_percentage(result, total_wait):
    """
    Baseado no resultado das waits define as porcentagens de cada
    :param result:
    :return:
    """
    for wait_class in result:
        result[wait_class] = 100 * float(result[wait_class])/float(total_wait)
    return result

def parse_perfdata(result):
    """
    Pega o dicionario com as informações e deixa legível para o Nagios
    :param result:
    :return:
    """
    perf_data = ''
    for wait_class in result:
        perf_data += str(wait_class) + '=' + str(result[wait_class]) + ' '
    return perf_data

def main():
    result = {}
    total_wait = 0
    args = parse_args()
    conn = estabConnection(args.user, args.pwd, args.sid, args.host, False)
    cur = conn.cursor()
    query = "select b.wait_class, nvl(sum(a.total_wait_time),0) total_wait \
             from \
              (SELECT NVL(a.event, 'ON CPU') AS event, \
                COUNT(*) AS total_wait_time \
                FROM   gv$active_session_history a \
                WHERE  a.sample_time > SYSDATE - 10/(24*60) \
                GROUP BY a.event)  \
              a right outer join gv$event_name b on (a.event = b.name) \
              where b.wait_class <> 'Idle' \
              group by b.wait_class \
              ORDER BY total_wait DESC"
    try:
        cur.execute(query)
    except:
        print "UNKNOWN - Erro ao executar a query!"
        sys.exit(3)
    for wait_class, time_waited in cur:
        total_wait += time_waited
        result[wait_class] = time_waited
    perf_data = parse_perfdata(result)
    cur.close()
    conn.close()
    print 'OK - Maior espera da base nos últimos 10 minutos é da classe ' + max(result.keys(), key=result.get)\
          + ' | '+ perf_data


if __name__ == '__main__':
    main()