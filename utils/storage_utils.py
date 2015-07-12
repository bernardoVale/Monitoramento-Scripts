#!/usr/bin/python
# coding=utf-8
# -------------------------------------------------------------
#  Dedicado a métodos que envolvam Filesystem e ASM
#
#       Autor: Bernardo S E Vale
#       Data Inicio:  20/06/2015
#       Data Release: 20/06/2015
#       email: bernardo.vale@lb2.com.br
#       Versão: v1.0
#       LB2 Consultoria - Leading Business 2 the Next Level!
import os

from utils.monitoramento_utils import Utils


class Storage:

    @staticmethod
    def asm_space(user, password, sid, diskgroup):
        """
        Calcula o tempo de disco
        caso seja um diskgroup ASM
        :param user: Usuario do oracle
        :param password: Senha do oracle
        :param sid: tnsnames de conexao
        :param diskgroup: Diskgroup dos archives
        :return: Espaco disponivel em bytes
        """
        global diskspace
        query = "set head off \n \
                set feedback off \n \
                col free_bytes format 999999999999999 \n \
                SELECT free_mb*1024*1024 as free_bytes \n \
                FROM v$asm_diskgroup \n \
                where name = '%s' \n \
                /" % diskgroup
        if user.lower() == 'sys':
            result = Utils.run_sqlplus(password, user, sid, query, True, True)
        else:
            result = Utils.run_sqlplus(password, user, sid, query, True, False)
        if 'ORA-' in result:
            print 'Erro desconhecido ao executar a query:' + result
            exit(3)
        try:
            diskspace = int(result.strip(' '))
        except:
            print 'Impossivel tratar o valor de espaco ASM. Verifique o nome do diskgroup'
            exit(3)
        return diskspace


    @staticmethod
    def filesystem_space_total(mountpoint):
        """
        Espaco total do disco
        :param mountpoint:
        :return:
        """
        global _st
        try:
            _st = os.statvfs(mountpoint)
        except:
            print 'UNKNOWN - Filesystem %s nao encontrado' % mountpoint
            exit(3)
        return _st.f_blocks * _st.f_frsize

    @staticmethod
    def filesystem_space(mountpoint):
        """
        Espaco em disco no mountpoint
        :param mountpoint:
        :return:
        """
        global _st
        try:
            _st = os.statvfs(mountpoint)
        except:
            print 'UNKNOWN - Filesystem %s nao encontrado' % mountpoint
            exit(3)
        return _st.f_bavail * _st.f_frsize


    @staticmethod
    def os_space_left(mountpoint_list):
        """
        Retorna o espaco livre total
        para uma lista de mountpoints
        :param mountpoint_list:
        :return:
        """
        _space_left = 0
        for mountpoint in mountpoint_list:
            _space_left += Storage.filesystem_space(mountpoint)
        return _space_left

    @staticmethod
    def os_space_total(mountpoint_list):
        """
        Retorna o espaco total
        para uma lista de mountpoints
        :param mountpoint_list:
        :return:
        """
        _space_left = 0
        for mountpoint in mountpoint_list:
            _space_left += Storage.filesystem_space_total(mountpoint)
        return _space_left

