# coding=utf-8
from utils.monitoramento_utils import Utils

__author__ = 'bernardovale'

# Query Depreciada devido a problemas de autoextend
# Ver issue #11 https://github.com/bernardoVale/Monitoramento-Scripts/issues/11

# query = "set head off \n \
#         set feedback off \n \
#         set linesize 80 \n \
#         set pages 500 \n \
#         set head off \n \
#         column tablespace_name format a20 \n \
#         column usage_pct       format 9999 \n \
#         column max_pct         format 9999 \n \
#         column autoextensible  format a5 \n \
#         break on report \n \
# select	/*+ PARALLEL (4) */ df.TABLESPACE_NAME, \n \
#         round(((df.BYTES - fs.BYTES) / df.BYTES) * 100) usage_pct, \n \
#         round(decode(df.MAXBYTES, 34359721984, 0, (df.BYTES - fs.BYTES) / df.MAXBYTES * 100)) max_pct, \n \
#         df.AUTOEXTENSIBLE \n \
# from \n \
#     ( \n \
#         select 	TABLESPACE_NAME, \n \
#                 sum(BYTES) BYTES, \n \
#                 AUTOEXTENSIBLE, \n \
#                 decode(AUTOEXTENSIBLE, 'YES', sum(MAXBYTES), sum(BYTES)) MAXBYTES \n \
#         from 	dba_data_files \n \
#         where tablespace_name not in ('UNDOTBS1','UNDOTBS2') \n \
#         group 	by TABLESPACE_NAME, \n \
#                 AUTOEXTENSIBLE \n \
#     ) \n \
#     df, \n \
#     ( \n \
#         select 	TABLESPACE_NAME, \n \
#                 sum(BYTES) BYTES \n \
#         from 	dba_free_space \n \
#         where tablespace_name not in ('UNDOTBS1','UNDOTBS2') \n \
#         group 	by TABLESPACE_NAME \n \
#     ) \n \
#     fs \n \
# where 	df.TABLESPACE_NAME=fs.TABLESPACE_NAME \n \
# order 	by df.TABLESPACE_NAME asc \n \
# /"

query = " set head off \n \
        set feedback off \n \
        WITH my_ddf AS \n \
    ( \n \
        SELECT file_id, tablespace_name, file_name, \n \
               DECODE (autoextensible, \n \
                       'YES', GREATEST (BYTES, maxbytes), \n \
                       BYTES \n \
                      ) mysize, \n \
              DECODE (autoextensible, \n \
                      'YES', CASE \n \
                         WHEN (maxbytes > BYTES) \n \
                            THEN (maxbytes - BYTES) \n \
                         ELSE 0 \n \
                      END, \n \
                      0 \n \
                     ) growth \n \
         FROM dba_data_files) \n \
SELECT   my_ddf.tablespace_name, \n \
         100 - ROUND (  (SUM (NVL (freebytes, 0)) + SUM (growth)) \n \
                 / SUM (my_ddf.mysize) \n \
                 * 100 \n \
               ) PERCENT_UTILIZADO, \n \
              'YES' \n \
    FROM my_ddf, (SELECT   file_id, SUM (BYTES) freebytes \n \
                      FROM dba_free_space \n \
                  GROUP BY file_id) dfs \n \
   WHERE my_ddf.file_id = dfs.file_id(+) \n \
         AND my_ddf.tablespace_name NOT LIKE '%UNDOTB%' \n \
GROUP BY my_ddf.tablespace_name;"


def main(sid, user, password, warning, critical, autoextend=None):
    m = Monitoring(sid, user, password, warning, critical, autoextend)
    if user.lower() == 'sys':
        result = Utils.run_sqlplus(password, user, sid, query, True, True)
    else:
        result = Utils.run_sqlplus(password, user, sid, query, True, False)
    if 'ORA-' in result:
        print 'UNKNOWN - Erro desconhecido ao executar a query:' + result
        exit(3)

    m.parse_result(result)
    m.build_tablespaces()
    m.check_if_ok()
    m.build_perfdata()
    m.finish_with_output()


class Monitoring:
    exit = 0
    perf_data = '| '
    critical_tablespaces = ''
    warning_tablespaces = ''
    warning_count = 0
    critical_count = 0
    tablespaces = []

    def __init__(self, sid, user, password, warning, critical, autoextend=None):
        self.sid = sid
        self.user = user
        self.password = password
        self.warning = warning
        self.critical = critical
        self.autoextend = autoextend

    # def check_autoextended_tablespace(self, tablespace):
    #     """
    #     Verifica a tablespace que é autoextended
    #     :param tablespace:
    #     :return:
    #     """
    #     if int(tablespace.pct_used) >= int(self.warning):
    #         self.exit = 1
    #         if int(tablespace.pct_used) >= int(self.critical):
    #             self.exit = 2
    #         self.append_tablespace_problem(tablespace.name, tablespace.pct_used)

    # def check_manual_tablespace(self, tablespace):
    #     """
    #     Verifica a tablespace que é manual
    #     :param tablespace:
    #     :return:
    #     """
    #     if int(tablespace.pct_used) >= int(self.warning):
    #         self.exit = 1
    #         if int(tablespace.pct_used) >= int(self.critical):
    #             self.exit = 2
    #         self.append_tablespace_problem(tablespace.name, tablespace.pct_used)

    # def check_if_ok(self):
    #     """
    #     Verifica se as tablespaces estao ok
    #     baseado nos thresholds
    #     :return:
    #     """
    #     if self.autoextend:
    #         for ts in self.tablespaces:
    #             if ts.autoextended == 'YES':
    #                 self.check_autoextended_tablespace(ts)
    #             else:
    #                 self.check_manual_tablespace(ts)
    #     else:
    #         for ts in self.tablespaces:
    #             self.check_manual_tablespace(ts)

    def check_tablespace(self, tablespace):
        """
        Verifica a tablespace e possiveis erros de size
        :param tablespace:
        :return:
        """
        if int(tablespace.pct_used) >= int(self.warning):
            self.exit = 1
            if int(tablespace.pct_used) >= int(self.critical):
                self.exit = 2
            self.append_tablespace_problem(tablespace.name, tablespace.pct_used)

    def check_if_ok(self):
        """
        Verifica se as tablespaces estao ok
        baseado nos thresholds
        :return:
        """
        for ts in self.tablespaces:
            self.check_tablespace(ts)

    def parse_result(self, r):
        """
        Realiza os tratamentos no resultado da query
        :type self: object
        :param r: Retorno da query
        :return: Lista com resultado formatado
        """
        self.result = r.strip()
        self.result = self.result.replace("|", " ")
        self.result = self.result.replace("     ", " ")
        self.result = self.result.replace("    ", " ")
        self.result = self.result.replace("   ", " ")
        self.result = self.result.replace("  ", " ")
        self.result = self.result.replace(' YES', ' YES ').split(' ')


    def build_tablespaces(self):
        """
        Constroi uma lista de tablespaces a partir
        da lista construida com o resultado
        da query
        """
        ts_tuples = zip(*[iter(self.result)] * 3)
        for i in ts_tuples:
            self.tablespaces.append(Tablespace(i))

    def append_tablespace_problem(self, name, pct_used):
        """
        Adiciona o nome e os valores das tablespaces
        para mencionar no output final
        :param name: Nome da tablespace
        :param pct_used: porcentagem de utilização
        :return:
        """
        if self.exit == 1:
            self.warning_count += 1
            self.warning_tablespaces += "%s %s%% " % (name, pct_used)
        else:
            self.critical_count += 1
            self.critical_tablespaces += "%s %s%% " % (name, pct_used)

    def finish_with_output(self):
        """
        Formatação do resultado final do script
        :return:
        """
        if self.exit == 0:
            print 'TABLESPACES OK %s' % self.perf_data
        elif self.exit == 1:
            print 'TABLESPACES WARNING - %s %s' % (self.warning_tablespaces, self.perf_data)
        elif self.exit == 2:
            print 'TABLESPACES CRITICAL - %s %s %s' % (self.warning_tablespaces,
                                                       self.critical_tablespaces, self.perf_data)
        exit(self.exit)

    def build_perfdata(self):
        """
        Constroi o valor do perdata
        :return:
        """
        self.perf_data += "{0:s}={1:s} {2:s}={3:s}".format('WARNING', str(self.warning_count),
                                                           'CRITICAL', str(self.critical_count))


class Tablespace:
    def __init__(self, ts):
        self.name, self.pct_used, _ = ts