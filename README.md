* cd docker-airflow
1. docker build -t puckel/docker-airflow:1.10.9 .
![](screen/1_airflow_image_build.PNG)
2. docker compose up
![](screen/2_docker_compose_up.PNG)
* cd ..
3. mvn clean package
![](screen/3_mvn_package.PNG)
4. docker build -t khan/weather:1.0 .
![](screen/4_docker_build_weather.PNG)
* Go to localhost:8080/admin/variable/
5. Add variable "weather_api" with key "https://api.weatherapi.com/v1/current.json?key=fcdf56c286944c8c8be150113210411&q=Minsk&aqi=no"
![](screen/5_airflow_var.PNG)
6. Manually trigger the DAG, wait for all 3 tasks to succeed
![](screen/6_airflow_run_dag.PNG)
7. View logs
![](screen/7_python_task_log.PNG)
![](screen/8_bash_task_log.PNG)
![](screen/9_docker_app_with_macros_task.PNG)