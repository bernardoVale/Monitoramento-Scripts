# coding=utf-8
import ctypes
import datetime
import os
import platform

__author__ = 'bernardovale'

class GrowthUtils:

    @staticmethod
    def get_date_hour():
        return datetime.datetime.now().strftime("%Y%m%d%H%M")
    @staticmethod
    def get_today():
        return datetime.datetime.now().strftime("%Y%m%d")

    @staticmethod
    def get_free_space_mb(p):
        """
        Returns the number of free bytes on the drive that p is on
        """
        global _st
        try:
            _st = os.statvfs(p)
        except:
            print 'UNKNOWN - Filesystem %s nao encontrado' % p
            exit(3)
        return _st.f_bavail * _st.f_frsize
# def file_to_string(my_file):
#     """
#     Retorna uma string com o arquivo
#     :param my_file: arquivo
#     :return:
#     """
#     with open(my_file) as f:
#         string = f.read()
#     return string
    #
    # @staticmethod
    # def collect_diskspace(my_file):
    #
    #     space = get_free_space_mb('/')
    #     day = get_date_hour()
    #     with open(my_file, 'a') as f:
    #         f.write("\n" + str(day) + "," + str(space))

    # @staticmethod
    # def get_last_four(my_file):
    #     """
    #     Pega os quatro últimos dias
    #     :param file:
    #     :return:
    #     """
    #     with open(my_file) as f:
    #         last_lines = f.readlines()[-4::]
    #     return last_lines

    # @staticmethod
    # def was_collected(my_file):
    #     """
    #     Verifica se no dia já foi feito a coleta do disco
    #     :param my_file:
    #     :return:
    #     """
    #     for coleta in file_to_string(my_file).split('\n'):
    #         if get_today() in coleta[0:8]:
    #             return True
    #     collect_diskspace(my_file)
    #     return False

# Caso windows descomente essa função e comente a de baixo
#
# def get_free_space_mb(folder):
#     """
#         Return folder/drive free space (in bytes)
#     """
#     if platform.system() == 'Windows':
#         free_bytes = ctypes.c_ulonglong(0)
#         ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
#         return free_bytes.value
#     else:
#         st = os.statvfs(folder)
#         return st.f_bavail * st.f_frsize/1024/1024

