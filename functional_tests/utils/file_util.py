# Copyright 2024 Broadcom. All Rights Reserved.
import os
from typing import AnyStr


def read_file(file_path: str) -> AnyStr:
    """
    Read and return the requested file.
    @param file_path: the file to read
    @type file_path: str
    @return: the requested file in str
    @rtype: dict
    """
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except IOError as e:
            raise Exception(f"IOError {file_path}': {e}")
    else:
        raise Exception(f"Missing file {file_path}")
