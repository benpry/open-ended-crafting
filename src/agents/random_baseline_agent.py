import random
from typing import Callable, Optional

import backoff
import pandas as pd
from requests import get, post

API_BASE = "http://localhost:8000"


class APIError(Exception):
    pass


@backoff.on_exception(
    backoff.expo,
    APIError,
    max_tries=5,
)
def call_api(method: Callable, *args, **kwargs):
    res = method(*args, **kwargs)  # type: ignore
    if res.status_code != 200:
        raise APIError(f"API call failed with status code {res.status_code}.")

    return res.json()


def update_inventory(inventory: list, action: tuple, new_item: Optional[dict]):
    item1, item2 = action
    if not item1["tool"]:
        inventory.remove(item1)
    if not item2["tool"]:
        inventory.remove(item2)

    if new_item is None:
        return inventory

    inventory.append(new_item)
    return inventory


def run_random_agent(domain: str, n_runs: int = 10, n_steps: int = 10):
    log = []
    for run_idx in range(n_runs):
        inv_response = call_api(
            get,
            f"{API_BASE}/api/init?domain={domain}",
        )
        inventory = inv_response["inventory"]

        for step in range(n_steps):
            item1, item2 = random.sample(inventory, 2)
            res = call_api(
                post,
                f"{API_BASE}/api/step?domain={domain}",
                json={
                    "action": (item1, item2),
                },
            )
            new_item = res["new_item"]
            inventory = update_inventory(inventory, (item1, item2), new_item)
            score = max([item["value"] for item in inventory])
            log.append(
                {
                    "run_idx": run_idx,
                    "timestep": step,
                    "action": (item1, item2),
                    "new_item": new_item,
                    "score": score,
                    "inventory": inventory,
                }
            )

    return pd.DataFrame(log)
