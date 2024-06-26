#!/usr/bin/env python3
import json

from config_modules_vmware.app import app

OPENAPI_FILE = "./docs/openapi.json"


def create_openapi_spec():
    with open(OPENAPI_FILE, "w+") as f:
        json.dump(app.openapi(), f, indent=1)


if __name__ == "__main__":
    create_openapi_spec()
