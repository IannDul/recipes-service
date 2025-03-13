#!/bin/sh
set -e

echo "Sleep 10 sec"
sleep 10

echo "Upgrade db by migrations"
alembic upgrade head

echo "Start of app..."
exec python3.10 main.py