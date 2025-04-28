import psycopg2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from logger import setup_logger

# Initialize the logger
logger = setup_logger()

base_path = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_path, "db")


def read_sql_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


verify_schema = os.path.join(db_path, "verify_schema.sql")
create_schema = os.path.join(db_path, "create_schema.sql")
verify_table = os.path.join(db_path, "verify_table.sql")
create_table = os.path.join(db_path, "create_table.sql")


def db_operations():
    try:
        logger.info(
            "Connecting to the database...",
            extra={"table": "violins", "step": "db_check"},
        )

        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = connection.cursor()

        logger.info(
            "Connection to the database successfully established!",
            extra={"table": "violins", "step": "db_check"},
        )

        cursor.execute(read_sql_file(verify_schema))
        if not cursor.fetchone():
            logger.info(
                "Schema 'violins' not found. Creating schema...",
                extra={"table": "violins", "step": "db_check"},
            )
            cursor.execute(read_sql_file(create_schema))
            connection.commit()
            logger.info(
                "Schema 'violins' created successfully.",
                extra={"table": "violins", "step": "db_check"},
            )

        cursor.execute(read_sql_file(verify_table))
        if not cursor.fetchone()[0]:
            logger.info(
                "Table 'violins_data' not found. Creating table...",
                extra={"table": "violins", "step": "db_check"},
            )
            cursor.execute(read_sql_file(create_table))
            connection.commit()
            logger.info(
                "Table 'violins_data' created successfully.",
                extra={"table": "violins", "step": "db_check"},
            )

        cursor.close()
        connection.close()
        logger.info(
            "Database operations completed and connection closed.",
            extra={"table": "violins", "step": "db_check"},
        )

    except Exception as e:
        logger.error(
            f"Error connecting to database: {e}",
            extra={"table": "violins", "step": "db_check"},
        )
        raise