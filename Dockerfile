# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONPATH "${PYTHONPATH}:${WORKDIR}"

# install dependencies
RUN apt-get update && apt-get install -y git postgresql && apt-get clean
RUN pip install --upgrade pip setuptools wheel

# install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# copy project
COPY ./app_streamlit /app/app_streamlit
COPY ./data /app/data

# setup toml server
EXPOSE 80
RUN mkdir ~/.streamlit &&  \
    cp app_streamlit/config.toml ~/.streamlit/config.toml &&  \
    cp app_streamlit/credentials.toml ~/.streamlit/credentials.toml

# start the app
CMD streamlit run app_streamlit/app.py
