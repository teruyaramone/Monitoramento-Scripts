# !/usr/bin/python
# coding=utf-8
import datetime
import json
from dbgrowth_utils import GrowthUtils
from monitoramento_utils import Utils


class Monitoring:
    def __init__(self, sid, user, password, disktime, asm=None, localdisk=None):
        self.sid = sid
        self.user = user
        self.password = password
        self.disktime = disktime
        self.asm = asm
        self.localdisk = localdisk
        self.growth_gather = 0
        self.gather_list = []
        self.days_left = 0
        self.diskspace = 0

    def db_growth(self):
        query = "set head off \n \
                set feedback off \n \
                SELECT  TRUNC(SUM((A.BYTES-B.BYTES))) TOTAL_UTILIZADO_SIZE \n \
                FROM \n \
                (   SELECT  x.TABLESPACE_NAME, SUM(x.BYTES) BYTES \n \
                        FROM    DBA_DATA_FILES x,DBA_TABLESPACES y \n \
                        WHERE y.CONTENTS <>'UNDO' \n \
                        AND x.TABLESPACE_NAME=y.TABLESPACE_NAME \n \
                        GROUP BY x.TABLESPACE_NAME) A, \n \
                (   SELECT  TABLESPACE_NAME, SUM(BYTES) BYTES \n \
                        FROM    DBA_FREE_SPACE \n \
                        GROUP BY TABLESPACE_NAME) B \n \
                WHERE  A.TABLESPACE_NAME=B.TABLESPACE_NAME;"

        if self.user.lower() == 'sys':
            result = Utils.run_sqlplus(self.password, self.user, self.sid, query, True, True)
        else:
            result = Utils.run_sqlplus(self.password, self.user, self.sid, query, True, False)
        if 'ORA-' in result:
            print 'Erro desconhecido ao executar a query:' + result
            exit(3)
        try:
            self.growth_gather = float(result.strip(' '))
            self.append_gather()
        except:
            print 'Impossivel tratar o valor da coleta'
            exit(3)

    def disktime_localdisk(self):
        """
        Calcula o tempo de disco em filesystem
        :return:
        """
        disk_list = self.disklist(self.localdisk)
        sum = 0
        for disk in disk_list:
            sum += GrowthUtils.get_free_space_mb(disk)
        self.diskspace = float(sum)
        self.days_left = int(self.diskspace / float(self.growth_avg))

    def disklist(self, diskstring):
        """
        Retorna uma lista de discos a partir da string
        :param diskstring:
        :return:
        """
        return str(diskstring).split(',')

    def calc_growth_avg(self):
        """
        Calcula o crescimento medio
        baseado nas ultimas quatro coletas
        :return:
        """
        i = 0
        variance = 0
        #todo Melhorar o metodo.Esta implementando media simples
        if len(self.gather_list) >= 4:
            aux_list = self.gather_list[-4:]
        elif len(self.gather_list) == 1:
            self.growth_avg = 1
            return
        else:
            aux_list = self.gather_list
        #-1 para n falhar com numero impar
        while i < len(aux_list) -1:
            value_0 = aux_list[i]['gather']
            value_1 = aux_list[i + 1]['gather']
            variance += value_1 - value_0
            i += 1
        #total = statistics.mean(gather['gather'] for gather in aux_list)
        #evitar divisao por 0 no calc no days_left
        if variance == 0:
            self.growth_avg = 1
        else:
            self.growth_avg = variance / len(aux_list)-1


    def append_gather(self):
        """
        Adiciona uma nova coleta ao json
        :return:
        """
        current_time = datetime.datetime.now().strftime("%Y%m%d")
        g = {'gather': self.growth_gather,
             'date': current_time
        }
        #Para impedir que adicione uma coleta do mesmo dia
        #somente uma necessaria
        for gather in self.gather_list:
            if gather['date'] == g['date']:
                return
        self.gather_list.append(g)

    def write_gather_json(self):
        """
        Escreve no disco o novo json de erros
        :return:
        """
        with open(Utils.fullpath('dbgrowth_data.json'), 'w') as f:
            try:
                json.dump(self.gather_list, f)
            except:
                print "UNKNOWN - Impossivel gravar JSON."
                exit(3)

    def open_gather_json(self):
        """
        Abre o JSON das coletas radicais
        clean_time
        :return:
        """
        gather_list = Utils.read_json(Utils.fullpath('dbgrowth_data.json'))
        self.gather_list = gather_list

    def exit_status(self):
        perf_data = '| DAYS_LEFT=%s AVG_GROWTH=%s DATABASE_SIZE=%s DISK_SPACE=%s' % \
                    (self.days_left,self.growth_avg,self.growth_gather,self.diskspace)
        if self.disktime:
            if self.days_left < 90:
                print 'WARNING - Menos de tres meses de espaco! %s ' % perf_data
                exit(1)
            else:
                print 'Crescimento OK %s' % perf_data
                exit(0)


def disktime_asm(args):
    print 'calculate ASM disktime'


def main(sid, user, password, disktime, asm=None, localdisk=None):
    args = ''
    m = Monitoring(sid, user, password, disktime, asm, localdisk)
    # pe de macaco
    i = 0
    m.open_gather_json()
    m.db_growth()
    m.write_gather_json()
    m.calc_growth_avg()
    if disktime:
        if asm == '' and localdisk == '':
            i = 1
        elif localdisk != '' and asm != '':
            i = 1
        if i == 1:
            print "Os parametros asm e localdisk nao podem ser utilizados juntos."
            exit(2)
        if asm != '':  #executando com ASM
            disktime_asm(args)
        elif localdisk != '':  #executando com localdisk
            m.disktime_localdisk()
    m.exit_status()