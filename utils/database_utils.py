from utils.monitoramento_utils import Utils


class Db:

    @staticmethod
    def single_int_query(user, password, sid, query):
        """
        Executa qualquer query que retorne 1 valor
        inteiro
        :param user: Usuario do oracle
        :param password: Senha do oracle
        :param sid: tnsnames de conexao
        :param query: Diskgroup dos archives
        :return:
        """
        global r
        if user.lower() == 'sys':
            result = Utils.run_sqlplus(password, user, sid, query, True, True)
        else:
            result = Utils.run_sqlplus(password, user, sid, query, True, False)
        if 'ORA-' in result:
            print 'Erro desconhecido ao executar a query:' + result
            exit(3)
        try:
            r_aux = result.strip(' ').replace(',', '.')
            if '.' in r_aux:
                r = int(round(float(r_aux)))
            else:
                r = int(r_aux)
        except:
            print 'Impossivel tratar o resultado da query: %s' % result
            exit(3)
        return r