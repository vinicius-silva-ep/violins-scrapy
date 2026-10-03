import os
import sys
from datetime import datetime
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from collect.run_spider import run_spider
from logger import setup_logger

# Initialize the logger
logger = setup_logger()


# Columns the spider is expected to yield. Checked up front so a broken or
# empty collect step names what is missing instead of raising a bare KeyError
# on whichever column the cleaning functions happen to touch first.
EXPECTED_COLUMNS = (
    "name",
    "price",
    "average_rating",
    "number_of_reviews",
    "stock",
    "description",
    "image",
    "category",
)


def extract_stock_number(stock_value: pd.Series) -> pd.Series:
    match = pd.Series(stock_value).str.extract(r"(\d+)")[0]
    return pd.to_numeric(match, errors="coerce").fillna(0).astype(int)


def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    df["price"] = (
        df["price"]
        .replace(r"[\$,]", "", regex=True)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )
    return df


def clean_numerical_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce").fillna(
        0
    )
    df["number_of_reviews"] = pd.to_numeric(
        df["number_of_reviews"], errors="coerce"
    ).fillna(0)
    return df


def transform_data() -> pd.DataFrame:
    try:
        logger.info(
            "Transforming data...",
            extra={"table": "violins", "step": "transform"},
        )    

        data = run_spider()

        df = pd.DataFrame(data)

        missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
        if missing:
            raise ValueError(
                f"Collected data is missing the columns {missing}. "
                f"Got {list(df.columns)} with {len(df)} rows."
            )

        df["date"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # Date format by ISO 8601 compatible with PostgreSQL

        df = clean_price(df)
        df = clean_numerical_columns(df)

        df["stock"] = extract_stock_number(df["stock"])

        logger.info(
            f"Transformed {len(df)} rows",
            extra={"table": "violins", "step": "transform"},
        )
        return df
    except Exception as e:
        logger.error(
            f"Error during data transformation: {e!r}",
            extra={"table": "violins", "step": "transform"},
            exc_info=True,
        )
        raise