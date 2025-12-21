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


class FeatureNameLLM(BaseModel):
    """
    Represents a single feature and all of its human-readable value names.
    Example: name="cook_level", values=["raw", "cooked", "overcooked"]
    """

    name: str = ""
    values: list[str] = Field(default_factory=list)


class ItemSemanticsLLM(BaseModel):
    emoji: str = ""
    name: str = ""


class ItemLLM(BaseModel):
    name: str = ""
    emoji: str = ""
    value: int = 0
    features: list[KV] = Field(default_factory=list)
    description: str = ""
    tool: bool = False
    ingredients: list[str] = Field(default_factory=list)


class ICExampleLLM(BaseModel):
    input: List[ItemLLM]
    outcome: ItemLLM
    semantics: ItemSemanticsLLM


class IngredientLLM(BaseModel):
    name: str = ""
    emoji: str = ""
    value: int = 0
    features: list[KV] = Field(default_factory=list)
    description: str = ""
    tool: bool = False


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
    feature_names: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map from feature name to list of string labels (index = value).",
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
    feature_names: list[FeatureNameLLM] = Field(
        default_factory=list,
        description="Feature names with ordered value labels.",
    )
    naming_ic_examples: List[ICExampleLLM] = Field(
        description="A list of in-context examples with input items and semantics."
    )


def kv_list_to_dict(items: list[KV]) -> dict[str, str]:
    return {kv.key: kv.value for kv in items}


def dict_to_kv_list(data: dict[str, Any]) -> list[KV]:
    return [KV(key=str(k), value=str(v)) for k, v in data.items()]


def feature_names_llm_list_to_dict(items: list[FeatureNameLLM]) -> dict[str, list[str]]:
    return {fn.name: fn.values for fn in items}


def feature_names_dict_to_llm_list(data: dict[str, list[str]]) -> list[FeatureNameLLM]:
    return [FeatureNameLLM(name=str(k), values=list(v)) for k, v in data.items()]


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


def item_from_llm(llm_item: ItemLLM) -> Item:
    if llm_item.tool:
        return Tool(name=llm_item.name, emoji=llm_item.emoji, tool=True)
    else:
        return NonTool(
            name=llm_item.name,
            emoji=llm_item.emoji,
            value=llm_item.value,
            features=kv_list_to_dict(llm_item.features),
            description=llm_item.description,
            tool=False,
        )


def ic_example_from_llm(llm_ic: ICExampleLLM) -> ICExample:
    return ICExample(
        input=[item_from_llm(i) for i in llm_ic.input],
        outcome=item_from_llm(llm_ic.outcome),
        semantics=ItemSemantics(
            emoji=llm_ic.semantics.emoji, name=llm_ic.semantics.name
        ),
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
        feature_names=feature_names_llm_list_to_dict(llm.feature_names),
        naming_ic_examples=[ic_example_from_llm(ic) for ic in llm.naming_ic_examples],
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


def ic_example_to_llm(example: ICExample) -> ICExampleLLM:
    return ICExampleLLM(
        input=[item_to_llm(item) for item in example.input],
        outcome=item_to_llm(example.outcome),
        semantics=ItemSemanticsLLM(
            emoji=example.semantics.emoji, name=example.semantics.name
        ),
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
        feature_names=feature_names_dict_to_llm_list(gd.feature_names),
        naming_ic_examples=[ic_example_to_llm(ic) for ic in gd.naming_ic_examples],
    )
