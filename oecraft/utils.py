from src.constants import CombinedItem, Ingredient, Item, Tool

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
