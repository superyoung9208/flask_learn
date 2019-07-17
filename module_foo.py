"""
File:module_foo.py
Author:laoyang
"""


def sayhello(to=None):
    if to:
        return 'Hello, %s!' % to
    return 'Hello!'
