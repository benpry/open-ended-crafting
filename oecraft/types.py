from typing import Annotated, Any, List, Tuple

from frozendict import frozendict
from pydantic import BaseModel, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.dataclasses import dataclass
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


class _FrozenDictPydanticAnnotation:
    """Custom Pydantic annotation for frozendict support."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Define how to validate frozendict."""

        def validate_frozendict(value: Any) -> frozendict:
            if isinstance(value, frozendict):
                return value
            if isinstance(value, dict):
                return frozendict(value)
            raise ValueError(f"Expected dict or frozendict, got {type(value)}")

        return core_schema.no_info_plain_validator_function(
            validate_frozendict,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: dict(x),
                info_arg=False,
                return_schema=core_schema.dict_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """Define the JSON schema as a plain object."""
        return {"type": "object"}


# Use this type annotation for frozendict fields in Pydantic models/dataclasses
FrozenDict = Annotated[frozendict, _FrozenDictPydanticAnnotation]


@dataclass(frozen=True)
class Item:
    name: str = ""
    emoji: str = ""


@dataclass(frozen=True)
class Tool(Item):
    pass


@dataclass(frozen=True)
class NonTool(Item):
    value: int = 0
    description: str = ""
    features: FrozenDict = Field(default_factory=frozendict)


@dataclass(frozen=True)
class Ingredient(NonTool):
    pass


@dataclass(frozen=True)
class CombinedItem(NonTool):
    ingredients: Tuple[Ingredient, ...] = Field(default_factory=tuple)


@dataclass(frozen=True)
class ItemSemantics:
    emoji: str
    name: str


@dataclass(frozen=True)
class ICExample:
    inputs: Tuple[Item, ...]
    outcome: Item
    semantics: ItemSemantics


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
        description="A list of ingredients that could appear in the player's starting inventory."
    )
    naming_system_prompt: str = Field(
        description="A string representing the system prompt for the small language model that will be used to assign names to the items given the names of the inputs and the features of the new item."
    )
    feature_names: dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map from feature name to list of string labels (index = value). Example: {'cook_level': ['raw', 'cooked', 'overcooked']}",
    )
    naming_ic_examples: List[ICExample] = Field(
        default_factory=list,
        description="A list of ICExamples representing the input and output features of the items in the game.",
    )
