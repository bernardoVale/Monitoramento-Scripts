#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from utils.database_utils import Db


__author__ = 'Bruno Teruya'
__copyright__ = 'LB2 Consultoria'

def main(sid, user, password, warning, critical):
    result = ''
    query = "set head off \n \
    set feedback off \n \
    select 1.0 valor from dual;"
    inicio = datetime.datetime.now()
    #time.sleep(11)
    Db.single_int_query(user, password, sid, query)

    fim = datetime.datetime.now()
    if 'ORA-' in result:
        print 'Erro desconhecido ao executar a query: %s' % result
        exit(3)
    else:
        intervalo = fim-inicio
        tempo = intervalo.days*24*60*60*1000
        tempo += intervalo.seconds*1000
        tempo += intervalo.microseconds/1000

        perf_data = 'CONNECTION_TIME=%d' % tempo
        if (int(tempo) >= int(critical)) :
            print 'CRITICAL - Conexao demorou %d milisegundos | %s ' % (tempo, perf_data)
            exit(3)
        elif (int(tempo) >= int(warning)) :
            print 'WARNING - Conexao demorou %d milisegundos | %s ' % (tempo, perf_data)
            exit(2)
        else:
            print 'OK - Conexao demorou %d milisegundos | %s ' % (tempo, perf_data)
            exit(0)

