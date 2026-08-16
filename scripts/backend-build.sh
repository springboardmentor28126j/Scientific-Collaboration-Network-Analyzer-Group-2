#!/bin/bash
set -e

echo "Installing backend dependencies..."
cd backend
pip install --no-cache-dir -r requirements.txt
echo "Backend build complete!"
