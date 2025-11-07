from .helpers import *

def run():
    data = load_data()
    data = tag(data)
    data = clean(data)
    data = combine(data)
    data = label(data)
    analyze(data)