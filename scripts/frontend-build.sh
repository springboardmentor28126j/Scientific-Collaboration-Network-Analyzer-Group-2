#!/bin/bash
set -e

echo "Installing frontend dependencies..."
cd frontend
pip install --no-cache-dir -r requirements.txt
echo "Frontend build complete!"
