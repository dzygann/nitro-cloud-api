#!/usr/bin/env bash

echo "nitro-cli.service: ## Starting ##" | systemd-cat -p info

export FLASK_APP=app.py

pipenv run flask --debug run -h 0.0.0.0
