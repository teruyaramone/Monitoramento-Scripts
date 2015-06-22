#!/usr/bin/python
__author__ = 'Bernardo Vale'
__enterprise__ = 'LB2 Consultoria e Teconologia S/S'
import os
import sys
import datetime
from datetime import date, timedelta

"""
    Definicao:
        Este script tem como funcao, verificar qualquer arquivo que tenha um padrao nominal

        arg1= -T bkp de hoje -Y bkp de ontem
        arg2= Local do arquivo
        arg3= Padrao do nome do arquivo
        arg4= pattern
        arg5= hora que o backup termina

        BackupCheck.py -T /home/bernardo/backup/ export_ ORA- 10
        -Y = yesterday backup
        -T = today backup
"""


class BackupCheck:
    now = datetime.datetime.now().strftime("%Y%m%d")
    yesterday = (datetime.datetime.now() - timedelta(1)).strftime("%Y%m%d")
    exit_var = 0
    def __init__(self, ignore_file):
        self.ignore_file = ignore_file
        pass

    def is_not_ignored(self, error):
        #Nao tem nada a ignorar
        if self.ignore_file is None:
            return True
        else:
            ignore_array = self.readFileToString(self.ignore_file).strip().split('\n')
            for line in ignore_array:
                if line in error:
                    return False
            return True

    def readFileToArray(self, file_dir):
        ins = open(file_dir, "r")
        array = []
        for line in ins:
            array.append(line)
        ins.close()
        return array

    def readFileToString(self, file_dir):
        ins = open(file_dir, "r")
        string = ""
        for line in ins:
            string += line
        ins.close()
        return string

    def find_log_pattern(self, logfile, pattern):
        log = BackupCheck.readFileToArray(self, logfile)
        errors_array = []
        for line in log:
            if pattern in unicode(line, 'utf-8') and self.is_not_ignored(line):
                errors_array.append(str(line).strip('\n')[:30] + '.' * 3)
        return errors_array

    def check_logs(self, log_dir, log_pattern, error_pattern, date_pattern):
        logs_analysed = dict()
        #Pega a lista de arquivos daquela pasta
        log_dir_files = os.listdir(log_dir)
        for log in log_dir_files:
            if log_pattern in log and date_pattern in log:
                logs_analysed[log] = self.find_log_pattern(log_dir + log, error_pattern)
                #Saindo com Warning
                if logs_analysed[log]:
                    self.exit_var = 1
        if len(logs_analysed) == 0:
            self.exit_var = 2 #Critical
            return "CRITICAL: Sem backups, favor verificar o servidor | Errors=0 Status=0;;;;"
        return self.format_return(logs_analysed)

    def format_return(self, logs):
        result = ""
        num_errors = 0
        num = 0
        for key, value in dict(logs).iteritems():
            result += "Backup: " + key + "\n"
            result += "Resultado: "
            if len(value) == 0:
                result += "OK"
            else:
                for error in value:
                    result += error + " "
                    num_errors += 1
            num += 1
            if num != len(dict(logs)):
                result += '\n'
        return result+'| Status=1 Erros=' + str(num_errors) + ';;;;'

    def backup_ready(self, bkp_time):
        now = datetime.datetime.now().strftime("%H")
        if now <= bkp_time:
            print 'Aguardando termino do backup | Status=0 Erros=0;;;;'
            exit(0)
        else:
            return True


def main(yesterday, path, name_pattern, error_pattern, finish_time, ignore_file=None):
    x = BackupCheck(ignore_file)
    if yesterday:
        print BackupCheck.check_logs(x, path, name_pattern, error_pattern, BackupCheck.yesterday)
    else:
        if BackupCheck.backup_ready(x, finish_time):
            print BackupCheck.check_logs(x, path, name_pattern, error_pattern, BackupCheck.now)
    exit(x.exit_var)
