# Deprecated Streamlit Frontend

This directory contains the archived Streamlit frontend code that has been deprecated in favor of the React frontend located in `/frontend`.

## Contents

- `app.py` - Main Streamlit application entry point
- `modules/` - Streamlit page modules:
  - `learning_mode.py` - Reading comprehension features
  - `grammar_practice.py` - Grammar practice interface
  - `view_history.py` - Session history viewer
  - `add_passage.py` - Passage addition interface
  - `admin_standards.py` - Admin tools
  - `reports.py` - Report generation
- `ui/` - Backend UI components that depended on Streamlit

## Migration

The application now uses:
- **Frontend**: React + Vite (`/frontend`)
- **Backend**: FastAPI (`/backend`)

## Do Not Use

This code is preserved for reference only. All new development should target the React frontend.
