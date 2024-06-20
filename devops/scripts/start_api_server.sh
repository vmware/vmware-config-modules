#!/bin/sh

set -e

echo "Starting gunicorn server"

if [ -z "${SERVER_CERT}"  ] || [ -z "${SERVER_KEY}" ]; then
   echo "No certificates provided."
   python3 -m gunicorn --workers 1 -k uvicorn.workers.UvicornWorker "config_modules_vmware.app:app" --timeout 60 --bind 0.0.0.0:80
else
   echo "Using ${SERVER_CERT} and ${SERVER_KEY} for https."
   python3 -m gunicorn --workers 1 -k uvicorn.workers.UvicornWorker "config_modules_vmware.app:app" --timeout 60 --bind 0.0.0.0:443 --certfile=/etc/ssl/certs/vmware/${SERVER_CERT} --keyfile=/etc/ssl/certs/vmware/${SERVER_KEY}
fi
