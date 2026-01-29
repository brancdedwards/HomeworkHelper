#!/bin/bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
