# README
# This Dockerfile is configured to create a docker container that can be run
# on AWS Batch as described at:
# https://aicure.atlassian.net/wiki/spaces/CDS/pages/2703622145/DBM+-+Batch+job+development
# IMPORTANT: It must be run from a root directory with the following structure:
# |- root
#     |- Dockerfile    <- Copy of this docker file up to the root directory
#     |-- aicurelib    <- Copy of aicurelib repo
#     |-- batch_base   <- Copy of batch_base repo
#     |-- pyannote-audio <- this repo
# 

ARG AWS_ACCOUNT_ID=272510231547
ARG AWS_REGION=us-west-2
FROM python:3.8

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# Above line may be a requirement for installing opencv-python
RUN apt-get install -y cmake --upgrade
RUN apt-get update && apt-get install -y ffmpeg python-tk

RUN pip install --upgrade pip
RUN pip install awscli

RUN aws configure set default.s3.signature_version s3v4
RUN aws configure set default.region us-west-2

RUN pip install pyarrow
# Needed for logging I think. Def need this one

RUN mkdir /vad
WORKDIR /vad
#COPY requirements.txt .

COPY ./aicurelib ./aicurelib
COPY ./batch_base ./batch_base
COPY ./pyannote-audio ./pyannote-audio

RUN pip install -e ./aicurelib
RUN pip install -e ./batch_base

RUN pip install -r ./pyannote-audio/requirements.txt

RUN pip install -e ./pyannote-audio

# Uncomment for batch docker production
ENTRYPOINT ["python", "./pyannote-audio/pyannote/aicure_vad/run_vad.py"]

# Uncomment for batch docker testing
# THIS CURRENTLY FAILS B/C OF RELATIVE PATH ISSUES AND B/C THE DOCKER CONTAINER
# DOES NOT HAVE AWS CREDENTIALS
# RUN pip install pytest-cov
# ENTRYPOINT ["pytest", "./pyannote-audio/tests/aicure_vad_test.py"]

