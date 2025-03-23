#!/bin/bash
echo "Starting build process..."
echo "Current directory: $(/bin/pwd)"
echo "Listing files: $(/bin/ls -la)"
pip install -r /vercel/path0/backend/TME_webAPI_DAAR/mySearchEngine/requirements.txt --verbose
echo "Installation completed."