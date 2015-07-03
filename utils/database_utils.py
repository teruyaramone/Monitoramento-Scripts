from monitoramento_utils import Utils


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
            r = int(result.strip(' '))
        except:
            print 'Impossivel tratar o resultado da query'
            exit(3)
        return r