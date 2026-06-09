import logging
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}


# Custom class to send logs to the PostgreSQL database.
class DBHandler(logging.Handler):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.conn = None
        self._connect()

    def _connect(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass

        self.conn = psycopg2.connect(
            host=self.db_config["host"],
            database=self.db_config["dbname"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            port=self.db_config["port"],
        )
        self.conn.autocommit = True
        self._create_table_if_needed()

    def _create_table_if_needed(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS violins.logs (
            id SERIAL PRIMARY KEY,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            table_name VARCHAR(100),
            step VARCHAR(100),
            log_type VARCHAR(50),
            message TEXT
        );
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(create_table_query)
        except Exception as e:
            print(f"Error while creating logs table: {e}")

    def _ensure_connection(self):
        if self.conn is None or self.conn.closed != 0:
            self._connect()

    def emit(self, record):
        try:
            if record.levelname == "DEBUG":
                return

            self._ensure_connection()
            log_message = self.format(record)
            log_type = record.levelname
            table = getattr(record, "table_name", "violins")
            step = getattr(record, "step", "default_step")

            query = """
                INSERT INTO violins.logs (log_type, message, table_name, step)
                VALUES (%s, %s, %s, %s)
            """
            with self.conn.cursor() as cursor:
                cursor.execute(query, (log_type, log_message, table, step))

        except Exception as e:
            print(f"Error while inserting into table: {e}")

    def close(self):
        """Closing the connection"""
        try:
            if self.conn is not None:
                self.conn.close()
        except Exception:
            pass
        finally:
            self.conn = None
        super().close()


def setup_logger():
    logger = logging.getLogger()

    # Avoid duplicate data
    if logger.hasHandlers():
        return logger

    # Creates the logs handler to the database
    db_handler = DBHandler(DB_CONFIG)
    db_handler.setLevel(logging.INFO)

    # Set up logging to use the handler
    logger.setLevel(logging.DEBUG)
    logger.addHandler(db_handler)

    # Console handle for terminal logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
