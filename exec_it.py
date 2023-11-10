import inspect

stuff = {}

with open("test.py","r") as f:
    code = f.read()


def inner():
    pass

def outer():
    inner()



outer()