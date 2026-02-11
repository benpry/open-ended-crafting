# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research project studying how LLM agents learn and communicate in an open-ended crafting game. Agents play crafting games across four domains (cooking, decorations, animals, potions), pass messages to future players, and the project analyzes how knowledge transfers through these chains. The package is called `oecraft`.

## Commands

```bash
# Install
pip install -e .

# Run tests
pytest tests/

# Run a single test
pytest tests/test_combination_functions.py

# Run simulations (LLM agents playing games in chains)
python scripts/run_simulations.py --domain cooking --agent_model gemini-2.5-flash --num-rounds 5 --num-chains 3 --chain-length 1

# Run the FastAPI server for interactive play
python scripts/run_server.py

# Tag messages with LM
python -m oecraft.lm_tagging --tagging_model fireworks/deepseek-v3p2

# Tag messages manually via CLI
python -m oecraft.manual_tagging --input data/human-data/experiment-1/processed/messages.csv
```

## Architecture

### Core Game Engine

- **`oecraft/types.py`** - Pydantic dataclasses for game objects: `Item`, `Tool`, `Ingredient`, `CombinedItem`, `GameDescriptor`. Items have `features` (stored as `frozendict`). `GameDescriptor` stores game rules as serialized Python source strings (combination_fn, value_fn, get_inventory_fn, descriptor_fn).
- **`oecraft/environment.py`** - `CraftingGame` (gymnasium Env) runs the core game loop. Tools are durable (stay in inventory); ingredients are consumed on use. `LMCraftingGame` wraps it for LLM interaction, managing prompt history via Google GenAI `types.Content` objects.
- **`oecraft/world_model.py`** - `MemoizedWorldModel` caches combination results and optionally calls an LLM to name combined items. The combination function is loaded from a string via `exec()`.
- **`oecraft/game_descriptors.py`** - Defines all four game domains. Each domain has: ingredients with features, tools, a combination function, a value function, an inventory selection function, and LLM naming prompts/examples. All exported via `GAME_DESCRIPTORS` dict.

### Key Design Patterns

- Game rules (combination_fn, value_fn, etc.) are defined as regular Python functions in `game_descriptors.py`, then serialized to strings via `inspect.getsource()` and stored in `GameDescriptor`. They're loaded back at runtime with `utils.load_function_from_string()` which uses `exec()`.
- The LLM agent uses the **Google GenAI SDK** (Gemini) for gameplay and the **Groq API** (via raw HTTP) for item naming. Message tagging uses **OpenAI SDK** (supports OpenAI, Fireworks, Gemini backends).
- `pyprojroot.here()` is used for resolving paths relative to the project root.

### Agents

- **`oecraft/agents/lm_agent.py`** - `CraftingAgent` uses Gemini to play games, producing JSON actions. After playing, writes a message for the next player. Requires `COCOLAB_GEMINI_API_KEY` env var.
- **`oecraft/agents/oracle_bfs_agent.py`** - BFS agent with perfect knowledge of game rules (no LLM needed for play).
- **`oecraft/agents/random_agent.py`** - Random baseline agent.

### Analysis Pipeline

- **`oecraft/lm_tagging.py`** - Tags messages on 7 dimensions (abstractions, concrete_recipes, positive/negative_valence, policy, dynamics, avoidance) using LLM.
- **`oecraft/optimization/simulation.py`** - Runs chains of agents passing messages, with checkpointing. `compute_simulation_statistics()` evaluates learning curves.
- **`notebooks/`** - Jupyter notebooks for data analysis and visualization.
- **`scripts/`** - Standalone scripts for running experiments, including SLURM scripts in `scripts/slurm/`.

## Environment Variables

- `COCOLAB_GEMINI_API_KEY` - Required for LLM agent gameplay
- `GROQ_API_KEY` - Used for item naming
- `OPENAI_API_KEY`, `FIREWORKS_AI_API_KEY`, `GEMINI_API_KEY` - Used for message tagging (depending on model choice)
