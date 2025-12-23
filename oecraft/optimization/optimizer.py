"""
A class to optimize the parameters of an experiment.
"""

import asyncio
import json
import os
import traceback
from typing import Callable, Optional

import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import (
    compute_simulation_statistics,
    inspect_sample_round,
    run_simulations,
)
from oecraft.types import GameDescriptor
from oecraft.utils import DotDict, load_function_from_string

# Import frozendict for validation
try:
    from frozendict import frozendict
except ImportError:
    frozendict = None


def _check_features_hashable(features: dict) -> tuple[bool, str]:
    """
    Check that all feature values are hashable (required for world model memoization).
    Returns (is_hashable, error_message).
    """
    if features is None:
        return True, ""

    for key, value in features.items():
        try:
            hash(value)
        except TypeError:
            return (
                False,
                f"Feature '{key}' has unhashable value of type {type(value).__name__}: {value}",
            )

    return True, ""


def _try_freeze_item(item) -> tuple[bool, str]:
    """
    Try to freeze an item (make it hashable) like the world model does.
    Returns (success, error_message).
    """
    from dataclasses import replace

    if item is None:
        return True, ""

    # Check if item has features
    features = getattr(item, "features", None)
    if features:
        is_hashable, err = _check_features_hashable(features)
        if not is_hashable:
            return False, err

        # Try to create frozendict
        if frozendict is not None:
            try:
                frozendict(features)
            except Exception as e:
                return False, f"Cannot freeze features: {e}"

    # Check ingredients for CombinedItem
    ingredients = getattr(item, "ingredients", None)
    if ingredients:
        for i, ing in enumerate(ingredients):
            success, err = _try_freeze_item(ing)
            if not success:
                return False, f"Ingredient {i}: {err}"

    # Try to hash the whole item with frozen features
    try:
        if features and frozendict is not None:
            frozen_item = replace(item, features=frozendict(features))
            if ingredients:
                frozen_item = replace(frozen_item, ingredients=tuple(ingredients))
            hash(frozen_item)
    except Exception as e:
        return False, f"Item cannot be hashed: {e}"

    return True, ""


def validate_game_descriptor(gd: GameDescriptor) -> tuple[bool, str]:
    """
    Validate that a game descriptor produces valid, runnable game mechanics.
    Returns (is_valid, error_message).
    """
    errors = []

    # 1. Try to compile and load all functions
    function_specs = [
        ("combination_fn", gd.combination_fn),
        ("value_fn", gd.value_fn),
        ("get_inventory_fn", gd.get_inventory_fn),
        ("descriptor_fn", gd.descriptor_fn),
    ]

    loaded_fns = {}
    for fn_name, fn_code in function_specs:
        try:
            loaded_fns[fn_name] = load_function_from_string(fn_code, fn_name)
        except SyntaxError as e:
            error_message = traceback.format_exc()
            errors.append(f"Syntax error in {fn_name}: {e}\nTraceback: {error_message}")
        except Exception as e:
            error_message = traceback.format_exc()
            errors.append(f"Error loading {fn_name}: {e}\nTraceback: {error_message}")

    if errors:
        return False, "\n".join(errors)

    # 2. Check that we have ingredients and tools
    if not gd.ingredients:
        errors.append("No ingredients defined")
    if not gd.tools:
        errors.append("No tools defined")

    if errors:
        return False, "\n".join(errors)

    # 3. Try to generate an inventory
    try:
        inventory = loaded_fns["get_inventory_fn"](4, gd.ingredients)
        if not inventory or len(inventory) == 0:
            errors.append("get_inventory_fn returned empty inventory")
    except Exception as e:
        error_message = traceback.format_exc()
        errors.append(f"Error in get_inventory_fn: {e}\nTraceback: {error_message}")

    if errors:
        return False, "\n".join(errors)

    # 4. Try to compute values for each ingredient
    try:
        for ingredient in inventory:
            value = loaded_fns["value_fn"](ingredient)
            if not isinstance(value, (int, float)):
                errors.append(
                    f"value_fn returned non-numeric value for {ingredient}: {value}"
                )
            elif value < 0 or value > 100:
                errors.append(
                    f"value_fn returned out-of-range value for {ingredient}: {value}"
                )
    except Exception as e:
        error_message = traceback.format_exc()
        errors.append(f"Error in value_fn: {e}\nTraceback: {error_message}")

    if errors:
        return False, "\n".join(errors)

    # 5. Try to get descriptions for each ingredient
    try:
        for ingredient in inventory:
            desc = loaded_fns["descriptor_fn"](ingredient, gd.feature_names)
            if not isinstance(desc, str):
                errors.append(
                    f"descriptor_fn returned non-string for {ingredient}: {desc}"
                )
    except Exception as e:
        error_message = traceback.format_exc()
        errors.append(f"Error in descriptor_fn: {e}\nTraceback: {error_message}")

    if errors:
        return False, "\n".join(errors)

    # 6. Try a simple combination (tool + ingredient) and verify result is hashable
    try:
        tool = gd.tools[0]
        ingredient = inventory[0]
        result = loaded_fns["combination_fn"](tool, ingredient)
        if result is not None:
            # Check value of combined item
            value = loaded_fns["value_fn"](result)
            if not isinstance(value, (int, float)):
                error_message = traceback.format_exc()
                errors.append(
                    f"value_fn returned non-numeric for combined item: {value}\nTraceback: {error_message}"
                )

            # Check that the result can be frozen/hashed (required for world model)
            success, err = _try_freeze_item(result)
            if not success:
                error_message = traceback.format_exc()
                errors.append(
                    f"combination_fn (tool + ingredient) produced unhashable item: {err}\nTraceback: {error_message}"
                )
    except Exception as e:
        error_message = traceback.format_exc()
        errors.append(
            f"Error in combination_fn (tool + ingredient): {e}\nTraceback: {error_message}"
        )

    if errors:
        return False, "\n".join(errors)

    # 7. Try combining two ingredients and verify result is hashable
    if len(inventory) >= 2:
        try:
            result = loaded_fns["combination_fn"](inventory[0], inventory[1])
            if result is not None:
                value = loaded_fns["value_fn"](result)
                if not isinstance(value, (int, float)):
                    errors.append(
                        f"value_fn returned non-numeric for combined ingredients: {value}"
                    )

                # Check that the result can be frozen/hashed
                success, err = _try_freeze_item(result)
                if not success:
                    errors.append(
                        f"combination_fn (ingredient + ingredient) produced unhashable item: {err}"
                    )
        except Exception as e:
            errors.append(f"Error in combination_fn (ingredient + ingredient): {e}")

    if errors:
        return False, "\n".join(errors)

    return True, ""


optimization_system_prompt = """You are designing the rules for a crafting game. In the games, the player plays for ten rounds. In each round, they have a starting inventory consisting of the two tools and four random ingredients. The player can use tools as many times as they would like, but ingredients are consumed when used. The player combines tools and ingredients to make new items, with the goal of creating the most valuable item they can. They can keep crafting items together as many times as they want, and the round ends when they press the "submit" button. The player's score for the round is the value of the most valuable item in their inventory at the time they submit, but it cannot drop below 0. The maximum possible value should always be 100. The way that item features are combined and how those features produce the value of an item are determined via Python functions. The names of items are assigned via a small language model that is given the names of the inputs and the features of the new item.

We can define specific games using the following GameDescriptor schema:

combination_fn: str
This is a string representing Python code that defines a function called combination_fn that takes two items and returns a new item. The returned item should always be of type Ingredient or CombinedItem. All feature values in returned items must be hashable (strings, ints, floats, None, or tuples, not lists or dicts). The items are memoized for efficiency.

value_fn: str
This is a string representing Python code that defines a function called value_fn that takes an item and returns a score between 0 and 100.

get_inventory_fn: str
This is a string representing Python code that defines a function called get_inventory_fn that takes a number of items and a list of all the ingredients and returns a list of items. It will be called to generate the starting inventories and can be used to enforce constraints on the starting inventory that make sure that a score of 100 is always achievable from any valid starting inventory.

descriptor_fn: str
This is a string representing Python code that defines a function called descriptor_fn that takes an item and returns a string describing the item. The string should nicely format the item's features.

tools: List[Tool]
This is a list containing the two tools in the game. Each tool should have a name, emoji, and description.

ingredients: List[Ingredient]
This is a list containing the ingredients in the game. Each ingredient should have a name, emoji, value, features, and description. Features should be a list of key-value pairs mapping the values of features (e.g. a cook level of 1) to their descriptions (e.g. "cooked"). IMPORTANT: All feature values must be hashable (strings, ints, floats, None - NOT lists or dicts).

naming_system_prompt: str
This is the system prompt for the small language model that will be used to assign names to the items given the names of the inputs and the features of the new item.

feature_names: dict[str, List[str]]
This is a list of feature names that lets us convert between integer-valued features and human-readable names. Each item in the list should have one of the features' names and a list of values. The ith element of the values list should be the human-readable name for the ith value of the feature.

naming_ic_examples: List[ICExample]
This is a list of in-context examples with input items and semantics. Each example should have an input list of items and an outcome item with a semantics.

Ideally, we would have an experiment where learning is fairly linear, where it's hard to do well on the first round and easy to do well on the last round, and there's not much variability in individual learning curves. We measure this using the mean squared error between the average scores on each round and an ideal learning curve that goes from 0 to 100 over 10 rounds. Your job will be to provide a game descriptor that minimizes this error. You will produce a game descriptor, then we will run simulated participants on that game and show you the results. Your job will then be to tweak the game descriptor to improve the results.
"""

propose_prompt = """Given the results of the last experiment and your reflection, please create a new game descriptor that will improve upon the current game. You should use the following dataclasses in writing the functions:

```python
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
```
"""

reflection_prompt = """We have run this experiment on simulated participants. Here are some metrics that will help you understand what happened in the experiment and decide how to tweak it in the next iteration. These metrics are the following:

- Loss: This is the main metric used to evaluate the game. It is the mean squared error between average scores on each round and an ideal learning curve that grows linearly from 0 to 100 plus the average standard deviation of the scores in each round. This is the main metric of interest, as it tells us how close the simulated participants' learning is to an ideal of linear growth and how consistently the participants show this growth. It is not realistic to get this metric all the way to 0, but we want it to be as low as possible.
- Average MSE per round: The MSE between the ideal learning curve and the mean scores of the simulated participants on each round. If the MSE is high, looking at this can tell you which rounds diverge most from ideal learning.
- Mean scores by round: The mean score of the simulated participants on each round. This lets you see what the learning curves look like.
- SD scores by round: The standard deviation of the scores of the simulated participants on each round. This metric is important because it captures the variability in learning across trials and simulated participants at each round. It isn't realistic to get this to 0, but we want it to be as low as possible.
- Linear model results: The results of a linear model fit to the scores of the simulated participants on each round. This metric is important because it tells us how close the simulated participants' learning is to an ideal of linear growth at each round. An ideal experiment would have a slope of 10 and an intercept of 0.
"human_history"
Your job is to reflect on the experiment results, decide what might have gone wrong, and propose a plan for how to tweak the game to improve the results. Do not provide a new game descriptor, just make a plan for how to improve the game.

Here are the results of the experiment:

## Aggregate Metrics
{metrics}

## Sample Gameplay
Below are samples of actual gameplay from early, middle, and late rounds. This shows what items were in the inventory, what actions the simulated participants took, and their reasoning. Use this to understand what strategies participants are using and where they might be getting stuck or confused.

### Early Round (Round 0) - Sample Gameplay
{sample_round_0}

### Middle Round (Round 4) - Sample Gameplay
{sample_round_4}

### Late Round (Round 9) - Sample Gameplay
{sample_round_9}
"""

validation_error_prompt = """The game descriptor you proposed has validation errors. Please fix these errors and try again.

Errors:
{errors}

Please provide a corrected game descriptor that fixes these issues."""


class ExperimentOptimizer:
    def __init__(
        self,
        model: str,
        sim_params: dict,
        run_name: str,
        checkpoint_dir: str = "data/optimization_checkpoints",
    ):
        self.curr_game_descriptor = None
        self.sim_params = sim_params
        self.history = []
        self.client = genai.Client(api_key=os.environ.get("COCOLAB_GEMINI_API_KEY"))
        self.run_name = run_name
        self.model = model
        self.iteration = 0
        self.log = []
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_path = os.path.join(
            checkpoint_dir, f"{run_name}_checkpoint.jsonl"
        )

    def _save_checkpoint(self):
        """Save the current log to a checkpoint file."""
        os.makedirs(self.checkpoint_dir, exist_ok=True)

        with open(self.checkpoint_path, "w") as f:
            for log_entry in self.log:
                f.write(json.dumps(log_entry) + "\n")

        print(f"Checkpoint saved to {self.checkpoint_path}")

    # @retry(stop=stop_after_attempt(15), wait=wait_exponential())
    def _generate_text(
        self,
        messages: list[dict],
        generate_kwargs: dict,
        tools: list[Callable] = [],
        response_schema: Optional[BaseModel] = None,
    ):
        response = self.client.models.generate_content(
            model=self.model,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=optimization_system_prompt,
                response_mime_type="application/json"
                if response_schema
                else "text/plain",
                response_schema=response_schema,
                tools=tools,
                **generate_kwargs,
            ),
        )

        return response

    def simulate(self):
        args = self.sim_params.copy()
        args.descriptor = self.curr_game_descriptor
        args.run_name = self.run_name + "_iteration_" + str(self.iteration)
        df_sims = asyncio.run(run_simulations(args))
        return df_sims

    def reflect(self, df_sims: pd.DataFrame):
        """
        Reflect on the simulation results and produce a diagnosis of what went wrong.
        """
        metrics = compute_simulation_statistics(df_sims)

        self.log.append(
            {
                "iteration": self.iteration,
                "stage": "metrics",
                "value": metrics,
            }
        )
        self._save_checkpoint()

        # Get sample gameplay from early, middle, and late rounds
        try:
            sample_round_0 = inspect_sample_round(df_sims, 0)
        except Exception as e:
            sample_round_0 = f"Could not retrieve sample: {e}"

        try:
            sample_round_4 = inspect_sample_round(df_sims, 4)
        except Exception as e:
            sample_round_4 = f"Could not retrieve sample: {e}"

        try:
            sample_round_9 = inspect_sample_round(df_sims, 9)
        except Exception as e:
            sample_round_9 = f"Could not retrieve sample: {e}"

        formatted_prompt = reflection_prompt.format(
            metrics=json.dumps(metrics, indent=2),
            sample_round_0=sample_round_0,
            sample_round_4=sample_round_4,
            sample_round_9=sample_round_9,
        )

        self.log.append(
            {
                "iteration": self.iteration,
                "stage": "reflection_prompt",
                "value": formatted_prompt,
            }
        )

        self.history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=formatted_prompt)],
            )
        )

        response = self._generate_text(
            self.history,
            generate_kwargs={"max_output_tokens": 32768},
        )
        reflection = response.text

        self.log.append(
            {
                "iteration": self.iteration,
                "stage": "reflection",
                "value": reflection,
            }
        )
        self._save_checkpoint()

        self.history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=reflection)],
            )
        )
        return reflection

    def propose(self, max_retries: int = 5):
        self.history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=propose_prompt)],
            )
        )

        for attempt in range(max_retries):
            response = self._generate_text(
                self.history,
                response_schema=GameDescriptor,
                generate_kwargs={"max_output_tokens": 32768},
            )

            self.history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.text)],
                )
            )

            self.log.append(
                {
                    "iteration": self.iteration,
                    "stage": "propose",
                    "value": response.text,
                }
            )

            try:
                new_descriptor = GameDescriptor.model_validate_json(response.text)
            except Exception as e:
                # JSON parsing or conversion error
                error_msg = f"Failed to parse game descriptor: {e}"
                self.log.append(
                    {
                        "iteration": self.iteration,
                        "stage": "propose_validation_error",
                        "attempt": attempt + 1,
                        "value": error_msg,
                    }
                )
                self._save_checkpoint()

                if attempt < max_retries - 1:
                    self.history.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(
                                    text=validation_error_prompt.format(
                                        errors=error_msg
                                    )
                                )
                            ],
                        )
                    )
                    continue
                else:
                    raise RuntimeError(
                        f"Failed to generate valid game descriptor after {max_retries} attempts: {error_msg}"
                    )

            # Validate the game descriptor
            is_valid, errors = validate_game_descriptor(new_descriptor)

            if is_valid:
                return new_descriptor
            else:
                self.log.append(
                    {
                        "iteration": self.iteration,
                        "stage": "propose_validation_error",
                        "attempt": attempt + 1,
                        "value": errors,
                    }
                )
                self._save_checkpoint()

                if attempt < max_retries - 1:
                    self.history.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(
                                    text=validation_error_prompt.format(errors=errors)
                                )
                            ],
                        )
                    )
                else:
                    raise RuntimeError(
                        f"Failed to generate valid game descriptor after {max_retries} attempts. Last errors:\n{errors}"
                    )

    def run(self, initial_game_descriptor: GameDescriptor, max_iter: int = 5):
        self.curr_game_descriptor = initial_game_descriptor
        self.log.append(
            {
                "iteration": self.iteration,
                "stage": "initial_game_descriptor",
                "value": initial_game_descriptor.model_dump_json(),
            }
        )
        self._save_checkpoint()

        self.history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="This is the initial game descriptor: "
                        + initial_game_descriptor.model_dump_json()
                    )
                ],
            )
        )

        for _ in range(max_iter):
            # simulate, reflect, and propose
            df_sims = self.simulate()
            self.reflect(df_sims)
            self.curr_game_descriptor = self.propose()
            self.iteration += 1

        # compute metrics on the final game descriptor
        df_sims = self.simulate()
        metrics = compute_simulation_statistics(df_sims)
        self.log.append(
            {
                "iteration": self.iteration,
                "stage": "metrics",
                "value": metrics,
            }
        )
        self._save_checkpoint()

        return self.log


if __name__ == "__main__":
    run_name = "potions_test_run"
    sim_params = DotDict(
        {
            "naming_model": "openai/gpt-oss-20b",
            "agent_model": "gemini-2.5-flash",
            "num_rounds": 10,
            "num_chains": 3,
            "chain_length": 1,
            "output_dir": "data/simulations",
            "verbose": False,
        }
    )
    optimizer = ExperimentOptimizer(
        model="gemini-3-pro-preview", sim_params=sim_params, run_name=run_name
    )
    potions_game_descriptor = GAME_DESCRIPTORS["potions"]
    log = optimizer.run(potions_game_descriptor, max_iter=1)
