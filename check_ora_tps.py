#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils.monitoramento_utils import Utils

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

def main(user, sid, password, warning):
    #sid, user, pwd, warning
        #parse_argsv2(sys.argv[1:])
    result = ''
    query = "set head off \n \
       set feedback off \n \
    SET SERVEROUTPUT ON \n \
        DECLARE \n \
        begindate date; \n \
        enddate date; \n \
        beginval number;\n \
        endval number;\n \
        begin \n \
             select sysdate, sum(value) \n \
    into begindate, beginval \n \
    from v$sysstat \n \
    where name in ('user commits','user_rollbacks'); \n \
    dbms_lock.sleep(5); \n \
    select sysdate, sum(value) \n \
    into enddate, endval \n \
    from v$sysstat  \n \
    where name in ('user commits','user_rollbacks'); \n \
    dbms_output.put_line( (endval-beginval) / ((enddate-begindate) * 86400)); \n \
    end; \n \
    /"
    if user.lower() == 'sys':
        result = Utils.run_sqlplus(password, user, sid, query, True, True)
    else:
        result = Utils.run_sqlplus(password, user, sid, query, True, False)
    perf_data = ''
    total = 0
    if 'ORA-' in result:
        print 'Erro desconhecido ao executar a query:'+result
        exit(3)
    else:
        perf_data = 'TPS=' + result
        if float(result.replace(',','.')) > int(warning):
            print 'WARNING - Quantidade de transações por segundo acima no normal. TPS:'+result+' | ' +perf_data
            exit(1)
        else:
            print 'OK - Transações por Segundo:' + result + ' | ' + perf_data