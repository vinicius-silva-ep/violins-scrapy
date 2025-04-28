import os
import sys
from sqlalchemy import create_engine

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SCHEMA
from transform.main import transform_data
from logger import setup_logger

# Initialize the logger
logger = setup_logger()


pwd = DB_PASSWORD
postgres_user = DB_USER
postgres_host = DB_HOST
postgres_port = DB_PORT
postgres_database = DB_NAME
postgres_schema = DB_SCHEMA


connection_string = f"cockroachdb+psycopg2://{postgres_user}:{pwd}@{postgres_host}:{postgres_port}/{postgres_database}"


def load_and_insert_data():
    try:
        logger.info(
            "Inserting data into table...",
            extra={"table": "violins", "step": "load"},
        )

        engine = create_engine(connection_string)

        # Transform the data
        df = transform_data()

        # Get the number of records to be inserted
        num_records = len(df)

        # Insert the data into the database
        df.to_sql(
            "violins_data", engine, schema=postgres_schema, if_exists="append", index=False
        )

    except Exception as e:
        logger.error(
            f"Error inserting data: {e}",
            extra={"table": "violins", "step": "load"},
        )
        raise