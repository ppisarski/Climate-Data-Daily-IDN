#!/usr/bin/env bash

source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:${PWD}"
streamlit run app_streamlit/app.py
deactivate
