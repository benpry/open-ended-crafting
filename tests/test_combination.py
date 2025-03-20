from src.model import combine_elements
import pytest


def test_combine_elements():
    e1 = "Raw steak"
    e2 = "Oven"
    print(combine_elements(e1, e2))
