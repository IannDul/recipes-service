#!/bin/sh
set -e

echo "Sleep 20 sec"
sleep 20

echo "Upgrade db by migrations"
alembic upgrade head

echo "Start of app..."
exec python3.10 main.py