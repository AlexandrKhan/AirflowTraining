from datetime import datetime

import boto3
import psycopg2
from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.decorators import apply_defaults
from smart_open import open


class S3ToPostgresDockerOperator(DockerOperator):
    @apply_defaults
    def __init__(self, aws_conn_id='aws_default', postgres_conn_id='postgres_default', **kwargs):
        self.aws_conn = BaseHook.get_connection(aws_conn_id)
        self.pg_conn = BaseHook.get_connection(postgres_conn_id)

        credentials = self.aws_conn
        kwargs['environment'] = dict(
            kwargs.pop('environment', {}),
            AWS_ACCESS_KEY=credentials.login,
            AWS_SECRET_KEY=credentials.password
        )
        super(S3ToPostgresDockerOperator, self).__init__(**kwargs)


aws_connection = BaseHook.get_connection("aws_default")
postgres_connection = BaseHook.get_connection("postgres_default")


def get_aws_conn(conn_id):
    connection = BaseHook.get_connection(conn_id)
    return connection


session = boto3.Session(
    aws_access_key_id=get_aws_conn('aws_default').login,
    aws_secret_access_key=get_aws_conn('aws_default').password,
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
                   'target_filename': 'countries_python.csv'},
        dag=dag
    )

    csv_to_postgres = PythonOperator(
        task_id='s3_csv_to_postgres',
        python_callable=csv_to_postgres,
        op_kwargs={'bucketname': 'epambucket',
                   'filename': 'countries_python'},
        dag=dag
    )

    java_unpack_csv = S3ToPostgresDockerOperator(
        task_id='java_s3_to_postgres',
        image='khan/s3postgres:1.0',
        api_version='auto',
        remove=True,
        docker_url='unix://var/run/docker.sock',
        network_mode='docker-airflow_default',
        command='epambucket countries.csv.gz'
    )

    unpack_zip >> csv_to_postgres >> java_unpack_csv
