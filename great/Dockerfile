FROM python:3.7-slim-buster

ADD requirements.txt ./
RUN apt-get update -yqq \
  && apt-get upgrade -yqq\
  && apt install vim -yqq\
  && apt-get install --no-install-recommends -yqq ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache \
  && pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && pip install sqlalchemy==1.3.24 \
  && pip install boto3==1.24.25 \
  && pip install botocore==1.27.25

ADD ./great_expectations ./great_expectations
