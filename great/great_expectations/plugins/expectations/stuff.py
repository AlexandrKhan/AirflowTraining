import os
from great_expectations.dataset import SqlAlchemyDataset
from sqlalchemy import create_engine

db_string = "postgres://airflow:airflow@localhost:5434/airflow"
db_engine = create_engine(db_string)

# Build up expectations on a table and save them
sql_dataset = SqlAlchemyDataset(table_name='countries_python', engine=db_engine)
sql_dataset.expect_column_values_to_not_be_null("id")
sql_dataset.save_expectation_suite("postgres_expectations.json")

# Load in a subset of the table and test it
sql_query = """
    select *
    from my_table
    where created_at between date'2019-11-07' and date'2019-11-08'
"""
new_sql_dataset = SqlAlchemyDataset(custom_sql=sql_query, engine=db_engine)
validation_results = new_sql_dataset.validate(
    expectation_suite="postgres_expectations.json"
)

if validation_results["success"]:
    ...