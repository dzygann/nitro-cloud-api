#!/bin/sh
echo "Starting bootstrap.sh"

# Assign an IP address to local loopback
ifconfig lo 127.0.0.1

# Run traffic forwarder in background and start the server
nohup python3 /app/traffic-forwarder.py 443 3 8000 &

python3 /app/secret-generator.py