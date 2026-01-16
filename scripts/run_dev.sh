#!/bin/bash
# Development server startup script

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run uvicorn with hot reload
uvicorn src.akitoi.api.main:app --reload --host 0.0.0.0 --port 8000
