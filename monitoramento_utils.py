#!/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
#       LB2 Monitoramento - Classe de utilitarios
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  29/09/2015
#       Data Release: 29/09/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------
import subprocess
import re

__author__ = 'bernardovale'

class Utils:

    def __init__(self):
        pass

    @staticmethod
    def run_sqlplus(pwd, user, sid, query, pretty, is_sysdba):
        """
        Executa um comando via sqlplus
        :param credencias: Credenciais de logon  E.g: system/oracle@oradb
        :param cmd: Query ou comando a ser executado
        :param pretty Indica se o usuário quer o resultado com o regexp
        :param Usuário é sysdba?
        :return: stdout do sqlplus
        """
        credencias = user +'/'+ pwd+'@'+sid
        if is_sysdba:
            credencias += ' as sysdba'
        session = subprocess.Popen(['sqlplus','-S',credencias], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        session.stdin.write(query)
        stdout, stderr = session.communicate()
        if pretty:
            r_unwanted = re.compile("[\n\t\r]")
            stdout = r_unwanted.sub("", stdout)
        if stderr != '':
            print stdout
            print 'ERRO - Falha ao executar o comando:' + query
            exit(2)
        else:
            return stdout