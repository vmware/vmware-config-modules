# Copyright 2024 Broadcom. All Rights Reserved.
import os

from paramiko.client import AutoAddPolicy
from paramiko.client import SSHClient
from scp import SCPClient

from functional_tests.utils.credential_api_client import Credential


class SshCommand(object):
    def __init__(self, credential: Credential):
        self.server = credential.hostname
        self.username = credential.username
        self.password = credential.password
        self.ssh = SSHClient()
        self.connect()

    def connect(self):
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(hostname=self.server, username=self.username, password=self.password)

    def send_cmd(self, cmd):
        print(f"ssh cmd {cmd}\n")
        stdin, stdout, stderr = self.ssh.exec_command(cmd)

        outlines = stderr.readlines()
        stderr_resp = "".join(outlines)
        print(f"stderr {stderr_resp}\n")
        outlines = stdout.readlines()
        stdout_resp = "".join(outlines)
        print(f"stdout {stdout_resp}\n")
        return stdout_resp, stderr_resp

    def close(self):
        self.ssh.close()

    def scp_get(self, remote_path, local_path):
        with SCPClient(self.ssh.get_transport()) as scp:
            print("scp from remote: local path {local_path} remote path: {remote_path}\n")
            scp.get(remote_path=remote_path, local_path=local_path)

    def scp_put(self, file, remote_path):
        with SCPClient(self.ssh.get_transport()) as scp:
            print("scp to remote: local file {file} remote path: {remote_path}\n")
            scp.put(os.path.expanduser(file), remote_path=remote_path)
