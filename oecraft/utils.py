import random
from dataclasses import asdict, replace
from typing import Any, Callable

from oecraft.types import CombinedItem, Ingredient, Item, NonTool, Tool

FIELDS_TO_REMOVE = ["id", "x", "y", "isLoading"]


def dict_to_dataclass(item: dict) -> Item:
    for field in FIELDS_TO_REMOVE:
        if field in item:
            del item[field]

    if item["tool"]:
        return Tool(**item)
    elif "ingredients" in item:
        item["ingredients"] = [dict_to_dataclass(x) for x in item["ingredients"]]
        return CombinedItem(**item)
    else:
        return Ingredient(**item)


def load_function_from_string(code: str, function_name: str) -> Callable:
    """
    Safely load a function from a string definition.
    """
    scope = {
        "random": random,
        "replace": replace,
        "asdict": asdict,
        "CombinedItem": CombinedItem,
        "Ingredient": Ingredient,
        "Item": Item,
        "Tool": Tool,
        "NonTool": NonTool,
        "Any": Any,
    }
    # We pass the scope as globals so that type hints in the function signature
    # (e.g. item: NonTool) can resolve correctly.
    exec(code, scope, scope)
    if function_name not in scope:
        raise ValueError(
            f"Function '{function_name}' not found in code string. "
            f"Available keys: {list(scope.keys())}"
        )
    return scope[function_name]


class DotDict(dict):
    """
    dot.notation access to dictionary attributes
    https://stackoverflow.com/a/23689767
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def copy(self):
        return DotDict(super().copy())
