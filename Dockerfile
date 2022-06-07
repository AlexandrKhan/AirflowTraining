FROM adoptopenjdk/openjdk11:jre-11.0.11_9-alpine
COPY target/WeatherAPIJava-1.0-SNAPSHOT.jar /usr/weather/WeatherAPIJava-1.0-SNAPSHOT.jar
WORKDIR /usr/weather
ENTRYPOINT ["java", "-jar", "WeatherAPIJava-1.0-SNAPSHOT.jar"]
