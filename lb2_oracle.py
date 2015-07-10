#!/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
#                 Scripts de Monitoramento do Oracle Database
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  29/05/2015
#       Data Release: 29/05/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------
import json
import os
import sys
import check_alert
import check_archives
import check_backup
import check_dbgrowth
import check_ora_tps
import check_ora_users
import check_tablespaces
import check_connection_time
from monitoramento_utils import Utils


class Database:
    def __init__(self, db_name, module):
        self.read_config(Utils.fullpath("monitoramento.json"))
        self.config_database(db_name, module)

    user = sid = password = ""
    module = {}
    cfg = ""

    def read_config(self, path):
        """
        Realiza a leitura do JSON e adiciona a variavel config.
        :param path: Local do json de config.
        :return: None
        """
        if Utils.file_exists(path):
            with open(path) as opf:
                try:
                    self.cfg = json.load(opf)
                except ValueError:
                    print "UNKNOWN - Impossivel ler arquivo de configuracao."
                    exit(3)
        else:
            print "UNKNOWN - Impossivel encontrar o arquivo de configuracao."

    def config_database(self, db_name, module):
        """
        Recebe o nome do banco e
        monta as suas diretivas
        :param db_name: Nome do banco que recebera o script
        :param module: Modulo que sera verificado
        :return:
        """
        for db in self.cfg['databases']:
            if db['sid'] == db_name:
                self.sid = db['sid']
                self.user = db['user']
                self.password = db['password']
                for m in db['modules']:
                    if m['name'] == module:
                        self.module = m
        if self.sid == '':
            print "UNKNOWN - Banco de dados não encontrado"
            exit(3)
        if self.module == {}:
            print "UNKNOWN - Modulo não encontrado"
            exit(3)

    def run_module(self):
        if self.module['name'] == 'tablespaces':
            check_tablespaces.main(self.sid, self.user, self.password,
                                   self.module['warning'], self.module['critical'],
                                   self.module['autoextend'])
        elif self.module['name'] == 'alertlog':
            check_alert.main(self.module['logfile'], self.module['clear_time']
                             , self.module['config'])
        elif self.module['name'] == 'tps':
            check_ora_tps.main(self.sid, self.user, self.password, self.module['warning'])
        elif self.module['name'] == 'users':
            check_ora_users.main(self.sid, self.user, self.password,
                                 self.module['warning'], self.module['sum']
                                 , self.module['schemas'])
        elif self.module['name'] == 'rman' or self.module['name'] == 'datapump':
            check_backup.main(self.module['yesterday'], self.module['path'],
                              self.module['name_pattern'], self.module['error_pattern'],
                              self.module['finish_time'], self.module['ignore_file'])
        elif self.module['name'] == 'dbgrowth':
            check_dbgrowth.main(self.sid, self.user, self.password,
                                self.module['disktime'], self.module['asm'],
                                self.module['localdisk'])
        elif self.module['name'] == 'archives':
            check_archives.main(self.sid, self.user, self.password,
                                self.module['warning'], self.module['critical'],
                                self.module['asm'], self.module['localdisk'])
        elif self.module['name'] == 'connection_time':
            check_connection_time.main(self.sid, self.user, self.password,
                                self.module['warning'], self.module['critical'])


def main(argv):
    db, m = parse_args(argv)
    database = Database(db, m)
    database.run_module()


def parse_args(argv):
    """
    Analisa os argumentos. Foi feito de maneira simples
    para nao ficar dependente do argparse
    :param argv: Argumentos do script
    :return: Tupla com os dois argumentos
    """
    global db_name, module
    if len(argv) == 2:
        db_name = argv[0]
        module = argv[1]
    # Esse pequeno artificio tem uma unica utilidade
    # o NRDS nao permite varios parametros separados
    # por espaco. Portanto adicionamos "-p" para
    # o NRDS tratar os proximos parametros
    elif len(argv) == 3 and argv[0] == '-p':
        db_name = argv[1]
        module = argv[2]
    else:
        print "Usage: ./lb2_oracle dbname module"
        exit(3)
    return db_name, module


if __name__ == '__main__':
    main(sys.argv[1:])