FROM adoptopenjdk/openjdk11:jre-11.0.11_9-alpine
COPY target/S3ToPostgres-1.0-SNAPSHOT-jar-with-dependencies.jar /usr/S3ToPostgres-1.0-SNAPSHOT.jar
WORKDIR /usr
ENTRYPOINT ["java", "-jar", "S3ToPostgres-1.0-SNAPSHOT.jar"]
