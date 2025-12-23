from typing import Annotated, Any, List, Tuple

from frozendict import frozendict
from pydantic import BaseModel, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.dataclasses import dataclass
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


def _dict_to_entries(d: dict) -> list:
    """Convert dict to list of {key, value} entries."""
    return [{"key": k, "value": v} for k, v in d.items()]


def _entries_to_dict(entries: list) -> dict:
    """Convert list of {key, value} entries to dict, parsing numeric strings."""
    result = {}
    for item in entries:
        value = item["value"]
        # Try to parse string values as numbers
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        result[item["key"]] = value
    return result


class _FrozenDictAnnotation:
    """Pydantic annotation for frozendict that avoids additionalProperties."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def validate(value: Any) -> frozendict:
            if isinstance(value, frozendict):
                return value
            if isinstance(value, dict):
                return frozendict(value)
            if isinstance(value, list):
                return frozendict(_entries_to_dict(value))
            raise ValueError(
                f"Expected dict, frozendict, or list of entries, got {type(value)}"
            )

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: _dict_to_entries(dict(x)),
                info_arg=False,
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, _handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
                "required": ["key", "value"],
            },
        }


FrozenDict = Annotated[frozendict, _FrozenDictAnnotation]


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
    inputs: Tuple[Tool | Ingredient | CombinedItem, ...]
    outcome: Tool | Ingredient | CombinedItem
    semantics: ItemSemantics


class _FeatureNamesAnnotation:
    """Pydantic annotation for feature_names dict that avoids additionalProperties."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def validate(value: Any) -> dict:
            if isinstance(value, dict):
                return value
            if isinstance(value, list):
                return {item["name"]: item["values"] for item in value}
            raise ValueError(f"Expected dict or list of entries, got {type(value)}")

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: [{"name": k, "values": v} for k, v in x.items()],
                info_arg=False,
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, _handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "values": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "values"],
            },
        }


FeatureNames = Annotated[dict, _FeatureNamesAnnotation]


class GameDescriptor(BaseModel):
    """A descriptor for the crafting game."""

    combination_fn: str = Field(
        description="Python code defining combination_fn(item1, item2) -> new_item"
    )
    value_fn: str = Field(
        description="Python code defining value_fn(item) -> score (0-100)"
    )
    get_inventory_fn: str = Field(
        description="Python code defining get_inventory_fn(n_items, all_ingredients) -> list of items"
    )
    descriptor_fn: str = Field(
        description="Python code defining descriptor_fn(item) -> description string"
    )
    tools: List[Tool] = Field(description="Tools available in the game")
    ingredients: List[Ingredient] = Field(description="Possible starting ingredients")
    naming_system_prompt: str = Field(
        description="System prompt for the LLM that names combined items"
    )
    feature_names: FeatureNames = Field(
        default_factory=dict,
        description="Map feature name -> list of labels. Example: {'cook_level': ['raw', 'cooked', 'burnt']}",
    )
    naming_ic_examples: List[ICExample] = Field(
        default_factory=list,
        description="In-context examples for item naming",
    )
