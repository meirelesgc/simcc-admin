import psycopg2
import psycopg2.extras

from ..config import settings

# Garantir que ele consiga converter UUID's
psycopg2.extras.register_uuid()


class Connection:
    def __init__(
        self,
        database: str = settings.ADM_DATABASE,
        user: str = settings.ADM_USER,
        password: str = settings.ADM_PASSWORD,
        host: str = settings.ADM_HOST,
        port: str = settings.ADM_PORT,
    ):
        self.database = database
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None

    def __connect(self):
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                host=self.host,
                password=self.password,
                port=self.port,
            )
            self.cursor = self.connection.cursor()
        except psycopg2.Error as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")

    def __close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def select(self, SCRIPT_SQL: str, parameters: list = []):
        self.__connect()
        query = None
        try:
            self.cursor.execute(SCRIPT_SQL, parameters)
            query = self.cursor.fetchall()
        except psycopg2.errors.InvalidTextRepresentation as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")
        except Exception as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")
        finally:
            self.__close()
        return query

    def exec(self, SCRIPT_SQL: str, parameters: list = []):
        self.__connect()
        try:
            self.cursor.execute(SCRIPT_SQL, parameters)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")
            self.connection.rollback()
            raise
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")
            self.connection.rollback()
            raise
        finally:
            self.__close()

    def execmany(self, SCRIPT_SQL: str, parameters: list = []):
        self.__connect()
        try:
            self.cursor.executemany(SCRIPT_SQL, parameters)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")
            self.connection.rollback()
            raise
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"\nTipo: {type(e).__name__}\nMensagem: {e}")
            self.connection.rollback()
            raise
        finally:
            self.__close()
