#!/bin/bash
cd "$(dirname "$0")"

# Uncomment and modify the line below as needed
# source ../[venv]/bin/activate

echo "Streamlit Init Flag --!"

streamlit run iot_dashboard.py --server.port=8501 --server.address=0.0.0.0
