#!/usr/bin/env python

# Plot raw and normalized variable for a selected month
# Map and distribution.

import os
import sys
import numpy as np
import tensorflow as tf

from utilities import plots
from tensor_utils import tensor_to_cube

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

from scipy.stats import gamma

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year", help="Year to plot", type=int, required=False, default=1969
)
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)
parser.add_argument(
    "--variable",
    help="Name of variable to use (psl, tas, ...)",
    type=str,
    default="pr",
)
args = parser.parse_args()


def load_tensor(file_name):
    sict = tf.io.read_file(file_name)
    imt = tf.io.parse_tensor(sict, np.float32)
    imt = tf.reshape(imt, [721, 1440])
    return imt


# Load the fitted values
raw = tensor_to_cube(
    load_tensor(
        "%s/DCVAE-Climate/raw_datasets/HG3/%s/%04d-%02d.tfd"
        % (os.getenv("SCRATCH"), args.variable, args.year, args.month)
    )
)
normalized = tensor_to_cube(
    load_tensor(
        "%s/DCVAE-Climate/normalized_datasets/ERA5/%s/%04d-%02d.tfd"
        % (os.getenv("SCRATCH"), args.variable, args.year, args.month)
    )
)


# Make the plot
fig = Figure(
    figsize=(10 * 3 / 2, 10),
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
font = {
    "family": "sans-serif",
    "sans-serif": "Arial",
    "weight": "normal",
    "size": 20,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
axb.set_axis_off()
axb.add_patch(
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor=(1.0, 1.0, 1.0, 1),
        fill=True,
        zorder=1,
    )
)

# choose actual and normalized data colour maps based on variable
cmaps = (cmocean.cm.balance, cmocean.cm.balance)
if args.variable == "pr":
    cmaps = (cmocean.cm.rain, cmocean.cm.tarn)
if args.variable == "psl":
    cmaps = (cmocean.cm.diff, cmocean.cm.diff)


ax_raw = fig.add_axes([0.02, 0.515, 0.607, 0.455])
if args.variable == "pr":
    vMin = 0
else:
    vMin = np.percentile(raw.data.compressed(), 5)
plots.plotFieldAxes(
    ax_raw,
    raw,
    vMin=vMin,
    vMax=np.percentile(raw.data.compressed(), 95),
    cMap=cmaps[0],
)

ax_hist_raw = fig.add_axes([0.683, 0.535, 0.303, 0.435])
plots.plotHistAxes(ax_hist_raw, raw, bins=25)

ax_normalized = fig.add_axes([0.02, 0.03, 0.607, 0.455])
plots.plotFieldAxes(
    ax_normalized,
    normalized,
    vMin=-0.25,
    vMax=1.25,
    cMap=cmaps[1],
)

ax_hist_normalized = fig.add_axes([0.683, 0.05, 0.303, 0.435])
plots.plotHistAxes(ax_hist_normalized, normalized, vMin=-0.25, vMax=1.25, bins=25)


fig.savefig("monthly.png")
