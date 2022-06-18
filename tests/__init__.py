import pytest


def test_print(capture_stdout):
    print("hello")
    assert capture_stdout["stdout"] == "hello\n"
