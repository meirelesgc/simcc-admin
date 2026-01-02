import psycopg2
import psycopg2.extras

from ..config import settings

psycopg2.extras.register_uuid()


class Connection:
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.connection = None
        self.cursor = None

    def __connect(self):
        try:
            if self.database_url:
                self.connection = psycopg2.connect(self.database_url)
            else:
                self.connection = psycopg2.connect(
                    database=settings.ADM_DATABASE,
                    user=settings.ADM_USER,
                    host=settings.ADM_HOST,
                    password=settings.ADM_PASSWORD,
                    port=settings.ADM_PORT,
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
