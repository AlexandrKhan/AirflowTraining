from datetime import datetime
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator

env = {
    'AWS_ACCESS_KEY_ID': '{{ var.value.AWS_ACCESS_KEY_ID }}',
    'AWS_SECRET_ACCESS_KEY': '{{ var.value.AWS_SECRET_ACCESS_KEY }}',
    'PG_HOST': '{{ var.value.PG_HOST }}',
    'PG_PORT': '{{ var.value.PG_PORT }}',
    'PG_USERNAME': '{{ var.value.PG_USERNAME }}',
    'PG_PASSWORD': '{{ var.value.PG_PASSWORD }}',
    'PG_DATABASE': '{{ var.value.PG_DATABASE }}'
}

with DAG("great_expectations",
         start_date=datetime(2022, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:

    great_expectations_docker = DockerOperator(
        task_id='ge_docker',
        image='great_expectations:0.15.18',
        api_version='auto',
        remove=True,
        environment=env,
        command='python /great_expectations/uncommitted/run_my_checkpoint.py',
        network_mode='host',
        docker_url='unix://var/run/docker.sock'
    )

    great_expectations_two_databases = DockerOperator(
        task_id='ge_docker_two_db',
        image='great_expectations:0.15.18',
        api_version='auto',
        remove=True,
        environment=env,
        command='python /great_expectations/ge_two_databases_compare.py',
        network_mode='host',
        docker_url='unix://var/run/docker.sock'
    )
    great_expectations_two_databases >> great_expectations_docker
