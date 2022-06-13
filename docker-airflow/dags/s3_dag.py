from datetime import datetime

import boto3
import psycopg2
from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python_operator import PythonOperator
from smart_open import open

aws_connection = BaseHook.get_connection("aws_default")
postgres_connection = BaseHook.get_connection("postgres_default")

session = boto3.Session(
    aws_access_key_id=aws_connection.login,
    aws_secret_access_key=aws_connection.password,
)

client = session.client('s3')


def unpack_and_copy_zip(bucketname, filename, target_filename):
    with open(f's3://{bucketname}/{filename}', transport_params=dict(client=client)) as fin:
        with open(f's3://{bucketname}/{target_filename}', 'w', transport_params=dict(client=client)) as fout:
            for line in fin:
                fout.write(line)


def csv_to_postgres(bucketname, filename):
    conn = psycopg2.connect(
        dbname=postgres_connection.schema,
        user=postgres_connection.login,
        password=postgres_connection.password,
        host=postgres_connection.host,
        port=postgres_connection.port
    )

    cur = conn.cursor()

    sql_create_table = f"""
    CREATE TABLE IF NOT EXISTS {filename}(
    """

    with open(f's3://{bucketname}/{filename}.csv', 'r',
              transport_params=dict(client=client)) as bucketfile:
        headers = next(bucketfile)
        column_list = headers.split(",")

        for column in column_list[:-1]:
            sql_create_table += f"""{column} VARCHAR, \n"""
        last_column = column_list[-1]
        sql_create_table += f"""{last_column} VARCHAR \n)"""

        print(sql_create_table)
        cur.execute(sql_create_table)
        cur.copy_from(bucketfile, f'{filename}', sep=",")

    cur.close()
    conn.commit()


with DAG("s3_to_postgres_dag",
         start_date=datetime(2022, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:
    unpack_zip = PythonOperator(
        task_id='unpack_zip',
        python_callable=unpack_and_copy_zip,
        op_kwargs={'bucketname': 'epambucket',
                   'filename': 'countries.csv.gz',
                   'target_filename': 'countries.csv'},
        dag=dag
    )

    csv_to_postgres = PythonOperator(
        task_id='s3_csv_to_postgres',
        python_callable=csv_to_postgres,
        op_kwargs={'bucketname': 'epambucket',
                   'filename': 'countries'},
        dag=dag
    )

    unpack_zip >> csv_to_postgres
