FROM python:3-slim

ARG BUILD_DATE                                                                                                                                                       
ARG VCS_REF

ENV PG_AIRFLOW_HOST postgres
ENV PG_AIRFLOW_PORT 5432
ENV PG_AIRFLOW_USER airflow
ENV PG_AIRFLOW_PASSWORD airflow
ENV PG_AIRFLOW_DATABASE airflow

ADD requirements.txt ./
RUN apt-get update -yqq \
  && apt-get install --no-install-recommends -yqq ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Run great_expectations
ADD ./great_expectations ./great_expectations
CMD ["great_expectations"]
