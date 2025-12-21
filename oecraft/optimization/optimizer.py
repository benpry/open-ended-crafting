"""
A class to optimize the parameters of an experiment.
"""

import asyncio
import os
from typing import Callable, Optional

import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel

from oecraft.game_descriptors import GAME_DESCRIPTORS
from oecraft.optimization.simulation import (
    compute_simulation_statistics,
    run_simulations,
)
from oecraft.types import (
    GameDescriptor,
    GameDescriptorLLM,
    game_descriptor_from_llm,
    game_descriptor_to_llm,
)
from oecraft.utils import DotDict

optimization_system_prompt = """You are designing the rules for a crafting game. In the games, the player plays for ten rounds. In each round, they have a starting inventory consisting of the two tools and four random ingredients. The player can use tools as many times as they would like, but ingredients are consumed when used. The player combines tools and ingredients to make new items, with the goal of creating the most valuable item they can. They can keep crafting items together as many times as they want, and the round ends when they press the "submit" button. The player's score for the round is the value of the most valuable item in their inventory at the time they submit, but it cannot drop below 0. The maximum possible value should always be 100. The way that item features are combined and how those features produce the value of an item are determined via Python functions. The names of items are assigned via a small language model that is given the names of the inputs and the features of the new item.

We can define specific games using the following GameDescriptor schema:

combination_fn: str
This is a string representing Python code that defines a function called combination_fn that takes two items and returns a new item.

value_fn: str
This is a string representing Python code that defines a function called value_fn that takes an item and returns a score between 0 and 100.

get_inventory_fn: str
This is a string representing Python code that defines a function called get_inventory_fn that takes a number of items and a list of all the ingredients and returns a list of items. It will be called to generate the starting inventories and can be used to enforce constraints on the starting inventory that make sure that a score of 100 is always achievable from any valid starting inventory.

descriptor_fn: str
This is a string representing Python code that defines a function called descriptor_fn that takes an item and returns a string describing the item. The string should nicely format the item's features.

tools: List[Tool]
This is a list containing the two tools in the game. Each tool should have a name, emoji, and description.

ingredients: List[IngredientLLM]
This is a list containing the ingredients in the game. Each ingredient should have a name, emoji, value, features, and description. Features should be a list of key-value pairs mapping the values of features (e.g. a cook level of 1) to their descriptions (e.g. "cooked").

naming_system_prompt: str
This is the system prompt for the small language model that will be used to assign names to the items given the names of the inputs and the features of the new item.

feature_names: list[FeatureNameLLM]
This is a list of feature names that lets us convert between integer-valued features and human-readable names. Each item in the list should have one of the features' names and a list of values. The ith element of the values list should be the human-readable name for the ith value of the feature.

naming_ic_examples: List[ICExampleLLM]
This is a list of in-context examples with input items and semantics. Each example should have an input list of items and an outcome item with a semantics.

's not much variability in individual learning curves. We measure this using the mean squared error between the average scores on each round and an ideal learning curve that goes from 0 to 100 over 10 rounds. Your job will be to provide a game descriptor that minimizes this error. You will produce a game descriptor, then we will run simulated participants on that game and show you the results. Your job will then be to tweak the game descriptor to improve the results.
"""

propose_prompt = """Given the results of the last experiment and your reflection, please create a new game descriptor that will improve upon the current game."""

reflection_prompt = """We have run this experiment on 20 simulated participants. Here are some metrics that will help you understand what happened in the experiment and decide how to tweak it in the next iteration. These metrics are the following:

- Loss: This is the main metric used to evaluate the game. It is the mean squared error between average scores on each round and an ideal learning curve grows linearly from 0 to 100 plus 0.1 times the average standard deviation of the scores in each round. This is the main metric of interest, as it tells us how close the simulated participants' learning is to an ideal of linear growth and how consistently the participants show this growth. It is not realistic to get this metric all the way to 0, but we want it to be as low as possible.
- Average MSE per round: The MSE between the ideal learning curve and the mean scores of the simulated participants on each round. If the MSE is high, looking at this can tell you which rounds diverge most from ideal learning.
- Mean scores by round: The mean score of the simulated participants on each round. This lets you see what the learning curves look like.
- SD scores by round: The standard deviation of the scores of the simulated participants on each round. This metric is important because it captures the variability in learning across trials and simulated participants at each round. It isn't realistic to get this to 0, but we want it to be as low as possible.
- Linear model results: The results of a linear model fit to the scores of the simulated participants on each round. This metric is important because it tells us how close the simulated participants' learning is to an ideal of linear growth at each round. An ideal experiment would have a slope of 1 and an intercept of 0.

Your job is to reflect on the experiment results, decide what might have gone wrong, and propose a plan for how to tweak the game to improve the results. Do not provide a new game descriptor, just make a plan for how to improve the game.

Here are the results of the experiment:

{metrics}
"""


class ExperimentOptimizer:
    def __init__(self, model: str, sim_params: dict, run_name: str):
        self.curr_game_descriptor = None
        self.sim_params = sim_params
        self.history = []
        self.client = genai.Client(api_key=os.environ.get("COCOLAB_GEMINI_API_KEY"))
        self.run_name = run_name
        self.model = model
        self.iteration = 0
        self.log = []

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

        self.history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=reflection_prompt.format(metrics=metrics))
                ],
            )
        )

        response = self._generate_text(
            self.history,
            # tools=[inspect_sample_round_tool],
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

        self.history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=reflection)],
            )
        )
        return reflection

    def propose(self):
        self.history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=propose_prompt)],
            )
        )

        response = self._generate_text(
            self.history,
            response_schema=GameDescriptorLLM,
            generate_kwargs={"max_output_tokens": 32768},
        )

        self.history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=response.text)],
            )
        )

        new_descriptor = GameDescriptorLLM.model_validate_json(response.text)

        self.log.append(
            {
                "iteration": self.iteration,
                "stage": "propose",
                "value": new_descriptor.model_dump_json(),
            }
        )

        return game_descriptor_from_llm(new_descriptor)

    def run(self, initial_game_descriptor: GameDescriptor, max_iter: int = 5):
        self.curr_game_descriptor = initial_game_descriptor
        self.history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="This is the initial game descriptor: "
                        + game_descriptor_to_llm(
                            initial_game_descriptor
                        ).model_dump_json()
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
        model="gemini-3-flash-preview", sim_params=sim_params, run_name=run_name
    )
    potions_game_descriptor = GAME_DESCRIPTORS["potions"]
    log = optimizer.run(potions_game_descriptor, max_iter=5)
    print(log)
