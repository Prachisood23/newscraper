#!/bin/bash
# Install Chrome
apt-get update && apt-get install -y google-chrome-stable
google-chrome --version
# Run the app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
