#!/bin/bash

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data
python app/initial_data.py
