import os
import sys

from src.exception import srcException
from src.logger import logging


def read_files(file_path):
    """
    Read the files in file path and return their contents as string
    Parameters:
        - file_path(str): Path to images
    Returns:
        - str: Text files
    """
    try:
        with open(file_path,'r') as file:
            content = file.read()
            return content
    except Exception as e:
        raise srcException(e, sys) from e