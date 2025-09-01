# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np
from datetime import timedelta

import pyseas
import pyseas.maps as psm
import pyseas.contrib as psc
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
from pathlib import Path

notebook_dir = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())

# %%
red = tuple(np.asarray([255, 0, 0]) / 255)
blue = tuple(np.asarray([0, 59, 118]) / 255)
orange = tuple(np.asarray([248, 186, 71]) / 255)
lgray = tuple(np.asarray([170, 170, 170]) / 255)

color_map = {
    "fishing": red,
    "mid_trawling": blue,
    "other": lgray,
    "other_fishing": orange,
}

prop = pyseas.styles.create_props(color_map.keys(), colors=list(color_map.values()))

mark_size = 2
title_font_size = 18
legend_font_size = 13
labels_font_size = 16


def plot_dots(df, mask, color):
    plt.plot(
        df.lon.values[mask],
        df.lat.values[mask],
        ".",
        markersize=mark_size,
        color=color,
        markeredgecolor=color,
        transform=psm.identity,
    )


def plot_track(df, gs, grid=0, title=""):

    if len(df):
        info = psc.track_state_panel(
            df.timestamp,
            df.lon,
            df.lat,
            df.label,
            plots=[
                {"label": "speed_knots", "values": df.speed_knots},
            ],
            gs=gs[grid],
            prop_map=prop,
        )
        for cat in ["fishing", "mid_trawling", "other_fishing"]:
            mask = df.label.values == cat
            plot_dots(df, mask, color_map[cat])

        labels = [k for k in info.legend_handles.keys() if k in color_map.keys()]
        handles = [
            info.legend_handles[k]
            for k in info.legend_handles.keys()
            if k in color_map.keys()
        ]

        info.map_ax.legend(labels=labels, handles=handles, fontsize=legend_font_size, labelcolor='black')
        info.map_ax.set_title(title, fontsize=title_font_size, color="black")
        info.map_ax.tick_params(axis="both", labelsize=labels_font_size, colors='black')
        for ax in info.plot_axes:
            for lbl in ax.get_xticklabels() + ax.get_yticklabels():
                lbl.set_fontsize(labels_font_size)
            ax.yaxis.label.set_fontsize(labels_font_size)

        for ax in info.plot_axes:
            for lbl in ax.get_xticklabels() + ax.get_yticklabels():
                lbl.set_fontsize(labels_font_size)
                lbl.set_color('black')  # set tick labels to black
            ax.xaxis.label.set_fontsize(labels_font_size)
            ax.xaxis.label.set_color('black')  # set x-axis label color
            ax.yaxis.label.set_fontsize(labels_font_size)
            ax.yaxis.label.set_color('black')  # set y-axis label color


def plot_tracks_multi(dfs, titles=[], save_to="plot", figsize=(8, 8)):
    length = len(dfs)

    with psm.context(psm.styles.panel):
        fig = plt.figure(figsize=figsize)
        gs = gridspec.GridSpec(1, length, figure=fig)

        for i in range(0, length):
            plot_track(dfs[i], gs, grid=i, title=titles[i])
    plt.savefig(save_to, dpi=1200, bbox_inches="tight")


# %%
# Confidential data provided by the authors of Hintzen et al. 2025
# Please ask them directly for this data
track = pd.read_csv(notebook_dir / "fig6b_track.csv")

# %%
track

# %%
df_fig6b = pd.read_csv(notebook_dir / "fig6bdata.csv")
timezone_adjust = 120
df_fig6b["haul_time_utc"] = pd.to_datetime(df_fig6b["haul_time"], utc=True) - timedelta(
    minutes=timezone_adjust
)
df_fig6b["shoot_time_utc"] = pd.to_datetime(
    df_fig6b["shoot_time"], utc=True
) - timedelta(minutes=timezone_adjust)

# %%

track = track.sort_values(by="timestamp")
track2 = track.copy()
track3 = track.copy()

track["label"] = track.label_general_model
track2["label"] = track2.label_trawler_model
track3["label"] = "other"

for _, row in df_fig6b.iterrows():
    track3.loc[
        (pd.to_datetime(track3.timestamp, utc=True) >= row.shoot_time_utc)
        & (pd.to_datetime(track3.timestamp, utc=True) <= row.haul_time_utc),
        "label",
    ] = "mid_trawling"

plot_tracks_multi(
    [track, track2, track3],
    figsize=(18, 10),
    titles=[
        "a) general model predictions",
        "b) trawler model predictions",
        "c) self-reported fishing",
    ],
    save_to=notebook_dir / "reply_plot.pdf",
)

plt.show()

# %%
