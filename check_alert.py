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

    def populate_errors(self):
        if Utils.file_exists('alertlog_errors.tmp'):
            with open('alertlog_errors.tmp', 'a') as f:
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

    def find_errors(self, line):
        for critical in self.issues.critical:
            if critical in line:
                self.error_list.append(line.replace('\n',''))
                self.critical_count += 1
                return
        for warning in self.issues.warning:
            if warning in line:
                self.error_list.append(line.replace('\n',''))
                self.warning_count += 1
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
    #print m.critical_count
    #print m.warning_count
    print m.error_list
