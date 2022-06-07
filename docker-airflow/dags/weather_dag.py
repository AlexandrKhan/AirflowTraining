from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator


def get_weather():
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
    }

    r = requests.get("https://api.weatherapi.com/v1/current.json?"
                     "key=fcdf56c286944c8c8be150113210411&q=Minsk&aqi=no",
                     headers=headers)
    data = r.json()
    return data


with DAG("weather_dag",
         start_date=datetime(2022, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:

    get_minsk_weather = PythonOperator(
        task_id="minsk_weather",
        python_callable=get_weather
    )

    weather_java = DockerOperator(
        task_id='docker_command',
        image='bash:3.1-alpine3.15',
        api_version='auto',
        remove=True,
        command='wget -O - "https://api.weatherapi.com/v1/current.json?'
                'key=fcdf56c286944c8c8be150113210411&q=Minsk&aqi=no"',
        network_mode='bridge',
        docker_url='unix://var/run/docker.sock',
        force_pull=True
    )

    weather_w_macros = DockerOperator(
        task_id='weather_docker',
        image='khan/weather:1.0',
        api_version='auto',
        remove=True,
        docker_url='unix://var/run/docker.sock',
        command='{{ var.value.weather_api }}',
        network_mode='bridge',
    )

    get_minsk_weather >> weather_java >> weather_w_macros
