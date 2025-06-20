# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: oecraft
#     language: python
#     name: python3
# ---

# %%
import numpy as np
import pandas as pd
import plotnine as p9
from pyprojroot import here

# %%
df_baseline = pd.read_csv(here("data/simulations/random_baseline_results.csv")).assign(
    timestep=lambda x: x["timestep"] + 1,
    run_idx=lambda x: pd.Categorical(x["run_idx"]),
    domain=lambda x: np.where(x["domain"] == "genetics", "species", x["domain"]),
)

# %%
df_baseline.columns

# %%
p = (
    p9.ggplot(
        df_baseline, p9.aes(x="timestep", y="score", color="run_idx", group="run_idx")
    )
    + p9.facet_wrap("domain")
    + p9.scale_x_continuous(breaks=range(1, 11))
    + p9.geom_point(position=p9.position_dodge(width=0.2), alpha=0.5)
    + p9.geom_line(
        position=p9.position_dodge(width=0.2),
        alpha=0.5,
    )
    + p9.geom_smooth(
        method="loess",
        mapping=p9.aes(group=1),
        size=1,
    )
    + p9.theme_minimal()
    + p9.theme(legend_position="none", plot_background=p9.element_rect(fill="white"))
)

p.save(here("figures/random_baseline.png"), width=10, height=6)
