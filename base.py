from io import StringIO
import urllib

import pandas as pd

import urllib.request

def read_instance(content):
    lines = content.strip().split("\n")[1:]
    data_str = ("\n".join([line.strip() for line in lines])).replace(" ",",")
    df = pd.read_csv(StringIO(data_str),header=None)
    return df

def read_instance_url(link):
    resource = urllib.request.urlopen(link)
    return read_instance(resource.read().decode(resource.headers.get_content_charset()))
