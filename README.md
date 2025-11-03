# Rate Comparison Portal

A Streamlit web application for rate comparison and smart top code checking.

## Features

### 📊 Rate Comparison
- Upload OLD and NEW rate files (CSV or Excel)
- Compare up to 3 rate pairs simultaneously
- Automatic percentage change calculation
- Visual indicators for rate increases/decreases

### 🧩 Smart Top Code Check
- Upload or use pre-loaded top codes file
- Compare area codes with comparison files
- 7-digit code matching
- Download matched and missing codes
- Preview and filtering capabilities

## How to Run Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run streamlit_app.py
```

## Deployment

This app is deployed on Streamlit Community Cloud.

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- openpyxl (for Excel file support)

