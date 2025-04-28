import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.load.db_check import db_operations
from src.load.main import load_and_insert_data
from logger import setup_logger

# Initialize the logger
logger = setup_logger()

def main():
    try:
        logger.info(
            "Starting database operations...",
            extra={"table": "your_table_name", "step": "general ETL"},
        )
        db_operations()
        logger.info(
            "Database operations completed successfully.",
            extra={"table": "your_table_name", "step": "general ETL"},
        )
    except Exception as e:
        logger.error(
            f"Error during database operations: {e}",
            extra={"table": "your_table_name", "step": "general ETL"},
        )
        return

    try:
        logger.info(
            "Starting data load and insert...",
            extra={"table": "your_table_name", "step": "general ETL"},
        )
        load_and_insert_data()
        logger.info(
            "Data load and insert completed successfully.",
            extra={"table": "your_table_name", "step": "general ETL"},
        )
    except Exception as e:
        logger.error(
            f"Error during data load and insert: {e}",
            extra={"table": "your_table_name", "step": "general ETL"},
        )
        return

if __name__ == "__main__":
    main()
