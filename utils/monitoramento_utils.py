# !/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
# LB2 Monitoramento - Classe de utilitarios
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  29/09/2015
#       Data Release: 29/09/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0a
#       LB2 Consultoria - Leading Business 2 the Next Level!
#---------------------------------------------------------------
import hashlib
import json
import subprocess
import re
import os
import sys
import imp
import traceback

__author__ = 'bernardovale'


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def file_exists(path):
        """
        Garante que o arquivo existe no SO
        :param path: Path do arquivo
        :return: Afirmação
        """
        # Agora tambem sei brincar de lambda
        x = lambda y: True if os.path.isfile(y) and os.access(y, os.R_OK) else False
        return x(path)

    @staticmethod
    def file_exists_not_empty(path):
        """
        Garante que o arquivo existe no SO
        e tambem nao esteja vazio
        :param path: Path do arquivo
        :return: Afirmação
        """
        x = lambda y: True if os.path.isfile(y) and os.access(y, os.R_OK) and os.stat(y).st_size != 0 else False
        return x(path)

    @staticmethod
    def run_sqlplus(pwd, user, sid, query, pretty, is_sysdba):
        """
        Executa um comando via sqlplus
        :param pwd: Senha do banco
        :param user: Usuario do banco
        :param sid: SID do banco (tnsnames.ora)
        :param query: Query ou comando a ser executado
        :param pretty: Indica se o usuário quer o resultado com o regexp
        :param is_sysdba: Usuário é sysdba?
        :return: stdout do sqlplus
        """
        credencias = user + '/' + pwd + '@' + sid
        if is_sysdba:
            credencias += ' as sysdba'
        session = subprocess.Popen(['sqlplus', '-S', credencias], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        session.stdin.write(query)
        stdout, stderr = session.communicate()
        if pretty:
            r_unwanted = re.compile("[\n\t\r]")
            stdout = r_unwanted.sub("", stdout)
        if stderr != '':
            print stdout
            print 'ERRO - Falha ao executar o comando:' + query
            exit(2)
        else:
            return stdout

    @staticmethod
    def read_json(path):
        """
        Realiza a leitura do JSON.
        :param path: Local do json de config.
        :return: None
        """
        if Utils.file_exists(path):
            with open(path) as opf:
                try:
                    return json.load(opf)
                except ValueError:
                    print "UNKNOWN - Impossivel ler arquivo de configuracao."
                    exit(3)
        else:
            print "UNKNOWN - Impossivel encontrar o arquivo de configuracao."
            exit(3)

    @staticmethod
    def fullpath(file_name):
        return "%s/%s" % (os.path.dirname(sys.argv[0]), file_name)

    @staticmethod
    def load_module(code_path):
        """
        Carrega um arquivo python.
        :param code_path: Local do arquivo python
        :return: Codigo compilado do modulo
        """
        global fin
        try:
            try:
                fin = open(Utils.fullpath(code_path), 'rb')
                return imp.load_source(hashlib.md5(Utils.fullpath(code_path)).hexdigest().upper(),
                                        Utils.fullpath(code_path), fin)
            finally:
                try:
                    fin.close()
                except:
                    pass
        except ImportError, x:
            traceback.print_exc(file=sys.stderr)
            raise
        except:
            traceback.print_exc(file=sys.stderr)
            raise