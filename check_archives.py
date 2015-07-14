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
from utils.database_utils import Db
from utils.storage_utils import Storage


class Monitoring:
    def __init__(self, sid, user, password, warning, critical, asm=None, localdisk=None):
        self.sid = sid
        self.user = user
        self.password = password
        self.asm = asm
        self.localdisk = localdisk
        self.warning = warning
        self.critical = critical
        self.growth_gather = 0
        self.gather_list = []
        self.diskspace = 0
        self.archives_used = 0
        self.disk_total = 0
        self.avg_archives = 0
        self.avg_archive_weight = 0
        self.disktime_left = 0
        self.archives_hour = 0
        self.archives_day = 0

    def parse_output(self):
        """
        Metodo para verificar como o script ira sair
        e de montagem do perf. data
        :return:
        """
        exit_var = 0
        output = "OK - Espaco disponivel para os archives dentro do aceitavel!"
        if self.critical >= self.disktime_left:
            exit_var = 2
            output = "CRITICAL - Disco de archives esgota em %s horas" % self.disktime_left
        elif self.warning >= self.disktime_left:
            exit_var = 1
            output = "WARNING - Disco de archives esgota em %s horas" % self.disktime_left
        perf_data = "| ARCHIVES_HR=%s ARCHIVES_DAY=%s " \
                    "TIME_LEFT(HR)=%s ARCHIVES_SPACE=%s ARCHIVES_USED_SPACE=%s" % (self.archives_hour,
                                                                                   self.archives_day,
                                                                                   self.disktime_left,
                                                                                   self.diskspace,
                                                                                   self.archives_used)
        print output, perf_data
        exit(exit_var)

    def time_left(self):
        """
        Calcula em horas quanto tempo
        demoraria para estourar o espaco em disco
        :return:
        """
        self.disktime_left = self.diskspace / (self.avg_archives * self.avg_archive_weight)

    def archives_by_hour(self):
        """
        Quantidade de archives gerados nesta hora
        :return:
        """
        query = "set head off \n \
                set feedback off \n \
                select trunc(count(*)/4) avg_archives from v$log_history \n \
                where trunc(first_time,'HH24') = trunc(sysdate,'HH24');"
        self.archives_hour = Db.single_int_query(self.user, self.password, self.sid, query)

    def archives_by_day(self):
        """
        Quantidade de archives gerados hoje
        :return:
        """
        query = "set head off \n \
                set feedback off \n \
                select trunc(count(*)/4) avg_archives from v$log_history \n \
                where trunc(sysdate,'DD') = trunc(first_time,'DD');"
        self.archives_day = Db.single_int_query(self.user, self.password, self.sid, query)

    def avg_archives_hour(self):
        """
        Calcula a media de archives por hora
        Pega a media de archives das ultimas 3 horas
        :return:
        """
        query = "set head off \n \
                set feedback off \n \
                select decode(trunc(count(*)/4),0,1,trunc(count(*)/4)) avg_archives from v$log_history \n \
                where trunc(first_time,'HH24') <= trunc(sysdate,'HH24') \n \
                and trunc(first_time,'HH24') >= trunc(sysdate,'HH24') - 3/24;"
        self.avg_archives = Db.single_int_query(self.user, self.password, self.sid, query)

    def current_archive_weight(self):
        """
        Verifica a media do tamanho de um unico
        archive
        :return:
        """
        query = "set head off \n \
                set feedback off \n \
                select nvl(avg(blocks*block_size),0) \n \
        from gv$archived_log h \n \
        where trunc(sysdate,'DD') = trunc(first_time,'DD');"
        self.avg_archive_weight = Db.single_int_query(self.user, self.password, self.sid, query)

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
        self.archives_used = Db.single_int_query(self.user, self.password, self.sid, query)

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

    def filesystem_space(self):
        """
        Espaco livre no filesystem
        :return:
        """
        disk_list = self.disklist(self.localdisk)
        sum = Storage.os_space_left(disk_list)
        self.diskspace = int(sum)
        #self.disk_total = Storage.os_space_left(disk_list)

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

def main(sid, user, password, warning, critical, asm=None, localdisk=None):
    m = Monitoring(sid, user, password, warning, critical, asm, localdisk)
    i = 0
    #m.archives_used_space()
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
    #print m.diskspace
    m.avg_archives_hour()
    m.current_archive_weight()
    m.time_left()
    m.archives_by_hour()
    m.archives_by_day()
    m.archives_used_space()
   # print 'Tamanho médio do archive:%s'  % m.avg_archive_weight
   # print 'Quantidade media de archives/hr:%s' % m.avg_archives
   # print 'Tempo de disco em horas:%s' % m.disktime_left
   # print 'Quantidade de archives nesta hora:%s' % m.archives_hour
   # print 'Quantidade de archives hoje:%s' % m.archives_day
   # print 'Espaco em archives agora: %s' % m.archives_used
    m.parse_output()
    #m.calc_usage_percent()
