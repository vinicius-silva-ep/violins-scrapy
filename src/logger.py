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
        self.conn = psycopg2.connect(
            host=db_config["host"],
            database=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config["port"],
        )
        self.cursor = self.conn.cursor()

        # Create table if not exists
        self.create_table()

    def create_table(self):
        """Creates the new table if not exists"""
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
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except Exception as e:
            print(f"Error while creating logs table: {e}")

    def emit(self, record):
        try:
            # Reject DEBUG records 
            if record.levelname == "DEBUG":
                return

            # Extract the log and level message

            log_message = self.format(record)
            log_type = record.levelname

            # Getting custom records or using default pattern            
            table = getattr(
                record, "table_name", "violins"
            )
            step = getattr(record, "step", "default_step")

            # Inserting log on the database
            query = """
                INSERT INTO violins.logs (log_type, message, table_name, step)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (log_type, log_message, table, step))
            self.conn.commit()

        except Exception as e:
            print(f"Error while inserting into table: {e}")

    def close(self):
        """Closing the connection"""
        self.cursor.close()
        self.conn.close()
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
