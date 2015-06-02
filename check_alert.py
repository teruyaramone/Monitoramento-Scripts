# coding=utf-8
# -------------------------------------------------------------
# Scripts de Monitoramento do Oracle Database
#
# Autor: Bernardo S E Vale
# Data Inicio:  01/06/2015
#       Data Release: 01/06/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------
import datetime
import json
import time
from monitoramento_utils import Utils


class Issues:
    warning = []
    critical = []

    def __init__(self, config):
        self.config = config
        self.build_issues()

    def build_issues(self):
        json = Utils.read_json(self.config)
        self.warning = json['warning']
        self.critical = json['critical']

class Monitoring:
    def __init__(self, logfile, clear_time, config, issues):
        self.logfile = logfile
        self.clear_time = clear_time
        self.config = config
        self.content = ''
        self.last_position = 0
        self.issues = issues
        self.warning_count = 0
        self.critical_count = 0
        self.error_list = []

    def error_is_cleared(self,error_date):
        """
        Verifica se o erro ja pode ser limpo
        :param error_date: Datetime
        :return: bool
        """
        clear_time = datetime.timedelta(minutes=self.clear_time)
        current_time = datetime.datetime.now()
        dt = datetime.datetime.strptime(error_date, "%Y%m%d%H%M")
        clear = dt + clear_time
        return True if clear < current_time else False

    def clear_old_errors(self):
        """
        Remove do JSON todos os erros que ja passaram do tempo
        clean_time
        :return:
        """
        error_list = Utils.read_json(Utils.fullpath('alertlog_errors.json'))
        error_list = [error for error in error_list if not self.error_is_cleared(error['date'])]
        self.error_list = error_list
        self.write_error_json()


    def write_error_json(self):
        """
        Escreve no disco o novo json de erros
        :return:
        """
        with open(Utils.fullpath('alertlog_errors.json'), 'w') as f:
            try:
                json.dump(self.error_list, f)
            except:
                print "UNKNOWN - Impossivel gravar JSON."
                exit(3)

    def append_error(self, error, is_critical):
        """
        Adiciona um novo erro a lista de erros
        :param error: Mensagem de erro
        :param is_critical: bool se é critico
        :return:
        """
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
        new_error = {'message' : error,
                     'date' : current_time,
                     'critical' : is_critical
        }
        self.error_list.append(new_error)

    def find_errors(self, line):
        for critical in self.issues.critical:
            if critical in line:
                err = line.replace('\n','')
                #self.error_list.append(err)
                self.critical_count += 1
                self.append_error(err, True)
                return
        for warning in self.issues.warning:
            if warning in line:
                err = line.replace('\n','')
                #self.error_list.append(err)
                self.warning_count += 1
                self.append_error(err, False)
                return

    def read_partial_file(self):
        if Utils.file_exists('check_alertlog.tmp'):
            with open('check_alertlog.tmp', 'r') as f:
                try:
                    f.seek(0)
                    file_content = f.readline()
                    self.last_position = int(file_content)
                except ValueError:
                    print "UNKNOWN - Impossivel ler logfile."
                    exit(3)
        else:
            with open('check_alertlog.tmp', 'a') as f:
                try:
                    f.write('0')
                    self.last_position = 0
                except:
                    print "UNKNOWN - Erro ao escrever check_alertlog.tmp. Verifique as permissoes."
                    exit(3)

    def read_log(self):
        count = 0
        if Utils.file_exists(self.logfile):
            with open(self.logfile) as f:
                for _ in xrange(int(self.last_position)):
                    next(f)
                for line in f:
                    self.find_errors(line)
                    count += 1
        if count > 0:
            self.update_log_position(count)
        else:
            print "Log OK - Sem novas informações"
            exit(0)

    def update_log_position(self, lines_read):
        """

        :param lines_read: Numero de linhas lidas
        """
        self.last_position = int(self.last_position) + int(lines_read)
        with open('check_alertlog.tmp', 'w') as f:
            try:
                f.write(str(self.last_position))
            except:
                print "UNKNOWN - Erro ao escrever check_alertlog.tmp. Verifique as permissoes."
                exit(3)


def main(logfile, clear_time, config):
    """
    Método inicial do script

    :param logfile: Caminho para o log
    :param clear_time: Tempo em minutos para limpar o último erro.
    :param config: Arquivo de configuração dos erros.
    :return:
    """
    i = Issues(config)
    m = Monitoring(logfile, clear_time, config, i)
    m.read_partial_file()
    m.read_log()
    m.clear_old_errors()
    #m.write_error_json()
    #print m.critical_count
    #print m.warning_count
    #print m.error_list
    #m.populate_errors()
