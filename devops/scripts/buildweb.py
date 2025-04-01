import argparse
import base64
import json
import os
import sys
import time

import urllib3


def submit_go_build(branch, release):
    go_build_username = os.getenv("GO_BUILD_USERNAME")
    go_build_api_key = os.getenv("GO_BUILD_API_KEY")
    # API credential is the username followed by apikey with the ":" delimit using the base64 encoding
    api_credential = base64.b64encode(f"{go_build_username}:{go_build_api_key}".encode("utf-8"))
    api_credential = "Basic " + api_credential.decode("utf8")
    headers = {
        "authorization": api_credential,
        "Accept": "application/json",
        "Referer": "http://buildweb.lvn.broadcom.net/queue/v2/enqueue/",
    }

    enqueue_data = {
        "branch": branch,
        "buildkind": "ob" if release else "sb",
        "buildtype": "release" if release else "beta",
        "changeset": "latest",
        "product": "config-modules",
        "sendemail": "false",
        "site": "lvn",
        "email": "[]",
        "requestor": go_build_username,
        "username": go_build_username,
    }

    http = urllib3.PoolManager()

    res = http.request(
        "POST", "http://buildweb.lvn.broadcom.net/queue/v2/enqueue/", headers=headers, fields=enqueue_data
    )
    print(f"Http Status {res.status}")
    if 201 == res.status:
        data_obj = json.loads(res.data.decode("utf-8"))
        build_id = data_obj["result"]
        build_url = data_obj["build_url"]
        print(
            f"Build: Release - {release}, Branch - {branch}, build-id - {build_id} scheduled successfully! {build_url}"
        )
        return build_id
    else:
        print(f"Error: Failed to submit a go build {res}")
        sys.exit(1)
    return res.result


def is_build_done(release, build_id):
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Referer": "http://buildweb.lvn.broadcom.net/",
    }
    build_type = "ob" if release else "sb"
    print(f"https://buildapi.lvn.broadcom.net/{build_type}/buildstateprogress/?build={build_id}&_format=json")
    http = urllib3.PoolManager()
    res = http.request(
        "GET",
        f"https://buildapi.lvn.broadcom.net/{build_type}/buildstateprogress/?build={build_id}&_format=json",
        headers=headers,
    )
    print(f"Http Status {res.status}")

    if 200 == res.status:
        data_obj = json.loads(res.data.decode("utf-8"))
        state_list = data_obj["_list"]
        last_state = state_list[-1]
        build_status = last_state["buildstate"]
        print(f"Build - build_type {build_type} {build_id}: {build_status}")
        build_status = build_status.lower()
        if build_status == "succeeded" or build_status == "not-needed":
            return True
        elif build_status == "invalid" or build_status == "failed":
            print(f"Error: build_status: {build_status}")
            sys.exit(1)
        else:
            return False
    else:
        print(f"Error: HTTP status 200 is expected instead of {res.status}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="trigger a go build job")
    parser.add_argument("-b", "--branch", help="git branch", required=True)
    parser.add_argument("-r", "--release", help="release?", required=True)
    args = parser.parse_args()
    print(f"Branch {args.branch}  release {args.release}")
    release = True if (args.release.lower() == "true") else False
    build_id = submit_go_build(branch=args.branch, release=release)

    while True:
        time.sleep(60)
        if is_build_done(release, build_id):
            return

    sys.exit(1)


if __name__ == "__main__":
    main()
