#!/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
#       LB2 Monitoramento - Verificacao de Users
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  29/09/2015
#       Data Release: 29/09/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------

from utils.monitoramento_utils import Utils

def wrap_schemas(schemas):
    """
    Pega a lista de usuarios e coloca no padrão SQL
    :param schemas: Lista de usuarios
    :return:
    """
    aux = ''
    for schema in schemas.split(','):
        aux += "'" + schema + "',"
    k = aux.rfind(",")
    return ''.join((aux[:k]+""))

def get_my_query(schemas,sum):
    """
    Retorna a query necessária para cada tipo de entrada
    Caso None deve adicionar somente os usuários do sistema
    :param schemas: Schemas a serem contados
    :param sum: Realiza somente a somatoria
    :return:
    """
    not_this_schemas = "'MGMT_VIEW','SYS','SYSTEM','DBSNMP','SYSMAN','OUTLN','FLOWS_FILES'\
,'MDSYS','WMSYS','APPQOSSYS','FLOWS_030000','APEX_030200','APEX_040200','APEX_050200','OWBSYS_AUDIT'\
,'OWBSYS','ORDDATA','ANONYMOUS','EXFSYS','XDB','ORDSYS','CTXSYS','ORDPLUGINS','OLAPSYS'\
,'SI_INFORMTN_SCHEMA','SCOTT','XS$NULL','MDDATA','ORACLE_OCM'\
,'DIP','APEX_PUBLIC_USER','SPATIAL_CSW_ADMIN_USR','SPATIAL_WFS_ADMIN_USR'"
    if sum:
        return "set head off \n \
                set feedback off \n \
                set pagesize 999 \n \
                set long 999 \n \
               select decode(COUNT(*),1,0,count(*)) from \
             dba_users inner join v$session using (username) \
              where username not in ("+not_this_schemas+");"
    if schemas != None:
        return "set head off \n \
                set feedback off \n \
                set pagesize 999 \n \
                set long 999 \n \
                select decode(COUNT(*),1,0,count(*)),username from \
             dba_users left outer join v$session using (username) \
              where username in ("+wrap_schemas(schemas)+")\
             group by username;"
    else:
        return "set head off \n \
                set feedback off \n \
                set pagesize 999 \n \
                set long 999 \n \
               select decode(COUNT(*),1,0,count(*)),username from \
             dba_users left outer join v$session using (username) \
              where username not in ("+not_this_schemas+")\
             group by username;"

def main(sid, user, password, warning, sum, schemas):
    #args = parse_args()
    query = get_my_query(schemas,sum)
    result = ''
    if user.lower() == 'sys':
        result = Utils.run_sqlplus(password, user, sid, query, True, True)
    else:
        result = Utils.run_sqlplus(password, user, sid, query, True, False)
    perf_data = ''
    total = 0
    if 'ORA-' in result:
        print 'Erro desconhecido ao executar a query:'+result
        exit(3)
    # Replace 4/3/2 whitespaces devido ao resultado do sqlplus,
    # split '' serve para criar a minha lista com cada coluna em um elemnto
    #strip para tirar os whites antes e dps.
    r = result.strip().replace("    "," ").replace("   "," ").replace("  "," ").split(' ')
    if sum:
        total = int(r[0])
    else:
        it = iter(r)
        for count, schema in zip(it,it):
            perf_data += schema + '=' + count + ' '
            total += int(count)
    perf_data += 'TOTAL='+str(total)+';'+warning
    if total > int(warning):
        print 'WARNING - Sobrecarga no banco, Sessoes:'+str(total)+' | ' +perf_data
        exit(1)
    else:
        print 'Total de Sessoes:' + str(total) + '| ' +perf_data
        exit(0)