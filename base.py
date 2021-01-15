# Base Functionality for Reading and Processing
import os
from io import StringIO

import pandas as pd

def read_instance(file):
    lines = open(f"{file}").read().strip().split("\n")[1:]
    data_str = ("\n".join([line.strip() for line in lines])).replace(" ",",")
    df = pd.read_csv(StringIO(data_str),header=None)
    return df
