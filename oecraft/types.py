from dataclasses import dataclass, field
from typing import Any, Union

from frozendict import frozendict
from pydantic import BaseModel


@dataclass(frozen=True)
class Item:
    name: str = ""
    emoji: str = ""


@dataclass(frozen=True)
class Tool(Item):
    tool: bool = True
    pass


@dataclass(frozen=True)
class NonTool(Item):
    value: int = 0
    features: Union[dict[str, Any], frozendict] = field(default_factory=dict)
    description: str = ""
    tool: bool = False


@dataclass(frozen=True)
class Ingredient(NonTool):
    pass


@dataclass(frozen=True)
class CombinedItem(NonTool):
    ingredients: list[Ingredient] = field(default_factory=list)


class GameDescriptor(BaseModel):
    """
    A descriptor for the crafting game.
    """

    combination_fn: str
    value_fn: str
    get_inventory_fn: str
    descriptor_fn: str
    tools: list[dict]
    ingredients: list[dict]
    naming_system_prompt: str
    feature_names: dict
    naming_ic_examples: list[dict]
