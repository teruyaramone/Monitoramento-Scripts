#!/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
#                 Scripts de Monitoramento - Archives
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  20/06/2015
#       Data Release: 20/06/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0
#       LB2 Consultoria - Leading Business 2 the Next Level!
from monitoramento_utils import Utils
from utils.storage_utils import Storage


class Monitoring:
    def __init__(self, sid, user, password, asm=None, localdisk=None):
        self.sid = sid
        self.user = user
        self.password = password
        self.asm = asm
        self.localdisk = localdisk
        self.growth_gather = 0
        self.gather_list = []
        self.diskspace = 0
        self.archives_used = 0
        self.disk_total = 0

    def archives_used_space(self):
        """
        Verifica o espaco utilizado pelos archives
        :return:
        """
        query = "set head off \n \
                set feedback off \n \
                select nvl(sum(blocks*block_size),0) \n \
                 from gv$archived_log \n \
                 where status IN ('A','X') \n \
                 and deleted = 'NO' \n \
                AND archived = 'YES';"
        if self.user.lower() == 'sys':
            result = Utils.run_sqlplus(self.password, self.user, self.sid, query, True, True)
        else:
            result = Utils.run_sqlplus(self.password, self.user, self.sid, query, True, False)
        if 'ORA-' in result:
            print 'Erro desconhecido ao executar a query:' + result
            exit(3)
        try:
            self.archives_used = int(result.strip(' '))
            print self.archives_used
        except:
            print 'UNKNOWN - Impossivel tratar o valor de espaco em archives'
            exit(3)

    def asm_space(self):
        """
        Espaco livre nos diskgroups ASM
        :return:
        """
        try:
            self.diskspace = Storage.asm_space(self.user, self.password, self.sid, self.asm)
        except:
            print 'UNKNOWN - Falha ao capturar o espaco em ASM'
            exit(3)
        print self.diskspace

    def filesystem_space(self):
        """
        Espaco livre no filesystem
        :return:
        """
        disk_list = self.disklist(self.localdisk)
        sum = Storage.os_space_left(disk_list)
        self.diskspace = int(sum)
        self.disk_total = Storage.os_space_total(disk_list)

    def disklist(self, diskstring):
        """
        Retorna uma lista de discos a partir da string
        :param diskstring:
        :return:
        """
        return str(diskstring).split(',')

    def calc_usage_percent(self):
        """
        Calcula em porcentagem a utilizacao
        do disco de archive
        :return:
        """
        total = Storage.filesystem_space_total(self.localdisk)
        aux = (total - self.diskspace) * 100 / total
        print 'Utilizacao em Porcentagem = %s' % aux

def main(sid, user, password, asm=None, localdisk=None):
    m = Monitoring(sid, user, password, asm, localdisk)
    i = 0
    m.archives_used_space()
    if asm == '' and localdisk == '':
        i = 1
    elif localdisk != '' and asm != '':
        i = 1
    if i == 1:
        print "Os parametros asm e localdisk nao podem ser utilizados juntos."
        exit(2)
    if asm != '':  #executando com ASM
       m.asm_space()
    elif localdisk != '':  #executando com localdisk
       m.filesystem_space()
    m.calc_usage_percent()
