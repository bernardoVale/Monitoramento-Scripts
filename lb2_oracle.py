#!/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
#                 Scripts de Monitoramento do Oracle Database
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  29/05/2015
#       Data Release: 11/07/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------
import json
import sys

from utils.monitoramento_utils import Utils


class Connection:
    def __init__(self, sid, user, password):
        self.sid = sid
        self.user = user
        self.password = password


class Database:
    def __init__(self, database, module_name):
        self.read_config(Utils.fullpath("config/monitoramento.json"))
        self.config_database(database, module_name)

    user = sid = password = ""
    script = ""
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

    def config_database(self, database, module_name):
        """
        Recebe o nome do banco e
        monta as suas diretivas
        :param database: Nome do banco que recebera o script
        :param module_name: Modulo que sera verificado
        :return:
        """
        for db in self.cfg['databases']:
            if db['sid'] == database:
                self.sid = db['sid']
                self.user = db['user']
                self.password = db['password']
                for m in db['modules']:
                    if m['name'] == module_name:
                        self.module = m
                        self.script = m['script']
        if self.sid == '':
            print "UNKNOWN - Banco de dados não encontrado"
            exit(3)
        if self.module == {}:
            print "UNKNOWN - Modulo não encontrado"
            exit(3)

    def run(self):
        """
        Chama o modulo especificado dinamicamente
        :return:
        """
        # Carregar o modulo dinamicamente
        module_name = Utils.load_module(self.script)
        #nao preciso desses valores no meu dict
        del [self.module['name'], self.module['script']]
        #Chamando a funcao main e passando seus parametros.
        #Importante verificar se o modulo tem o metodo main
        if hasattr(module_name, 'main'):
            #Construo um set com o nome de todos os parametros do metodo main
            m_variables = set(module_name.main.func_code.co_varnames)
            t = set(['sid', 'user', 'password'])
            #O Objetivo e verificar se o metodo precisa desses parametros
            if t.issubset(m_variables):
                getattr(module_name, 'main')(sid=self.sid, user=self.user, password=self.password, **self.module)
            else:
                # Se ele nao precisa de conexao com o banco so passo os argumentos que o modulo pediu
                getattr(module_name, 'main')(**self.module)
        else:
            print 'UNKNOWN - Modulo nao implementou o metodo obrigatorio main()'
            exit(3)


def main(argv):
    db, m = parse_args(argv)
    database = Database(db, m)
    database.run()


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
        print "Usage: ./lb2_oracle.py dbname module"
        exit(3)
    return db_name, module


if __name__ == '__main__':
    main(sys.argv[1:])