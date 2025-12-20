from typing import Any, List

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


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
    features: dict[str, Any] = Field(default_factory=dict)
    description: str = ""
    tool: bool = False


@dataclass(frozen=True)
class Ingredient(NonTool):
    pass


@dataclass(frozen=True)
class CombinedItem(NonTool):
    ingredients: list[Ingredient] = Field(default_factory=list)


@dataclass(frozen=True)
class ItemSemantics:
    emoji: str
    name: str


@dataclass(frozen=True)
class ICExample:
    input: List[Item]
    outcome: Item
    semantics: ItemSemantics


class KV(BaseModel):
    key: str
    value: str


class ItemLLM(BaseModel):
    name: str
    emoji: str
    value: int
    features: list[KV]
    description: str
    tool: bool
    ingredients: list[str]


class IngredientLLM(BaseModel):
    name: str
    emoji: str
    value: int
    features: list[KV]
    description: str
    tool: bool


class GameDescriptor(BaseModel):
    """
    A descriptor for the crafting game.
    """

    combination_fn: str = Field(
        description="A string representing Python code that defines a function called combination_fn that takes two items and returns a new item."
    )
    value_fn: str = Field(
        description="A string representing Python code that defines a function called value_fn that takes an item and returns a score between 0 and 100."
    )
    get_inventory_fn: str = Field(
        description="A string representing Python code that defines a function called get_inventory_fn that takes a number of items and a list of all the ingredients and returns a list of items."
    )
    descriptor_fn: str = Field(
        description="A string representing Python code that defines a function called descriptor_fn that takes an item and returns a string describing the item."
    )
    tools: List[Tool] = Field(description="A list of tools in the game.")
    ingredients: List[Ingredient] = Field(
        description="A list of ingredients in the game."
    )
    naming_system_prompt: str = Field(
        description="A string representing the system prompt for the small language model that will be used to assign names to the items given the names of the inputs and the features of the new item."
    )
    feature_names: dict[str, Any] = Field(
        default_factory=dict,
        description="Key/value list describing feature names.",
    )
    naming_ic_examples: List[ICExample] = Field(
        description="A list of lists of key-value pairs representing the input and output features of the items in the game."
    )


class GameDescriptorLLM(BaseModel):
    """
    A descriptor for the crafting game.
    """

    combination_fn: str = Field(
        description="A string representing Python code that defines a function called combination_fn that takes two items and returns a new item."
    )
    value_fn: str = Field(
        description="A string representing Python code that defines a function called value_fn that takes an item and returns a score between 0 and 100."
    )
    get_inventory_fn: str = Field(
        description="A string representing Python code that defines a function called get_inventory_fn that takes a number of items and a list of all the ingredients and returns a list of items."
    )
    descriptor_fn: str = Field(
        description="A string representing Python code that defines a function called descriptor_fn that takes an item and returns a string describing the item."
    )
    tools: List[ItemLLM] = Field(description="A list of tools in the game.")
    ingredients: List[IngredientLLM] = Field(
        description="A list of ingredients in the game."
    )
    naming_system_prompt: str = Field(
        description="A string representing the system prompt for the small language model that will be used to assign names to the items given the names of the inputs and the features of the new item."
    )
    feature_names: list[KV] = Field(
        description="Key/value list describing feature names.",
    )


def kv_list_to_dict(items: list[KV]) -> dict[str, str]:
    return {kv.key: kv.value for kv in items}


def dict_to_kv_list(data: dict[str, Any]) -> list[KV]:
    return [KV(key=str(k), value=str(v)) for k, v in data.items()]


def item_to_llm(item: Item) -> ItemLLM:
    features = getattr(item, "features", {}) or {}
    description = getattr(item, "description", "")
    value = getattr(item, "value", 0)
    tool_flag = getattr(item, "tool", False)
    ingredients = getattr(item, "ingredients", []) or []
    return ItemLLM(
        name=item.name,
        emoji=item.emoji,
        value=value,
        features=dict_to_kv_list(features),
        description=description,
        tool=tool_flag,
        ingredients=[ing.name for ing in ingredients],
    )


def ingredient_from_llm(llm_ing: IngredientLLM) -> Ingredient:
    return Ingredient(
        name=llm_ing.name,
        emoji=llm_ing.emoji,
        value=llm_ing.value,
        features=kv_list_to_dict(llm_ing.features),
        description=llm_ing.description,
        tool=llm_ing.tool,
    )


def tool_from_llm(llm_tool: ItemLLM) -> Tool:
    return Tool(
        name=llm_tool.name,
        emoji=llm_tool.emoji,
        tool=True,
    )


def game_descriptor_from_llm(llm: GameDescriptorLLM) -> GameDescriptor:
    return GameDescriptor(
        combination_fn=llm.combination_fn,
        value_fn=llm.value_fn,
        get_inventory_fn=llm.get_inventory_fn,
        descriptor_fn=llm.descriptor_fn,
        tools=[tool_from_llm(t) for t in llm.tools],
        ingredients=[ingredient_from_llm(ing) for ing in llm.ingredients],
        naming_system_prompt=llm.naming_system_prompt,
        feature_names=kv_list_to_dict(llm.feature_names),
        naming_ic_examples=[],  # currently unused in optimization loop
    )


def ingredient_to_llm(ing: Ingredient) -> IngredientLLM:
    return IngredientLLM(
        name=ing.name,
        emoji=ing.emoji,
        value=ing.value,
        features=dict_to_kv_list(getattr(ing, "features", {}) or {}),
        description=getattr(ing, "description", ""),
        tool=getattr(ing, "tool", False),
    )


def tool_to_llm(tool: Tool) -> ItemLLM:
    return ItemLLM(
        name=tool.name,
        emoji=tool.emoji,
        value=getattr(tool, "value", 0),
        features=[],
        description=getattr(tool, "description", ""),
        tool=True,
        ingredients=[],
    )


def game_descriptor_to_llm(gd: GameDescriptor) -> GameDescriptorLLM:
    return GameDescriptorLLM(
        combination_fn=gd.combination_fn,
        value_fn=gd.value_fn,
        get_inventory_fn=gd.get_inventory_fn,
        descriptor_fn=gd.descriptor_fn,
        tools=[tool_to_llm(t) for t in gd.tools],
        ingredients=[ingredient_to_llm(ing) for ing in gd.ingredients],
        naming_system_prompt=gd.naming_system_prompt,
        feature_names=dict_to_kv_list(gd.feature_names),
    )
