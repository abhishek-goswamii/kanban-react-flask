#!/bin/bash
set -e

echo "running migrations..."
alembic upgrade head

echo "starting backend..."
exec python run.py
