from __future__ import print_function

import os
import sys
import logging

import pandas as pd
import numpy as np

from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from scipy.stats.stats import pearsonr

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler


file_path = os.path.dirname(os.path.realpath(__file__))
# lib_path = os.path.abspath(os.path.join(file_path, '..'))
# sys.path.append(lib_path)
lib_path2 = os.path.abspath(os.path.join(file_path, "..", "..", "common"))
sys.path.append(lib_path2)

import candle

logger = logging.getLogger(__name__)
candle.set_parallelism_threads()

additional_definitions = [
    {"name": "latent_dim", "action": "store", "type": int, "help": "latent dimensions"},
    {
        "name": "residual",
        "type": candle.str2bool,
        "default": False,
        "help": "add skip connections to the layers",
    },
    {
        "name": "reduce_lr",
        "type": candle.str2bool,
        "default": False,
        "help": "reduce learning rate on plateau",
    },
    {
        "name": "warmup_lr",
        "type": candle.str2bool,
        "default": False,
        "help": "gradually increase learning rate on start",
    },
    {"name": "base_lr", "type": float, "help": "base learning rate"},
    {
        "name": "epsilon_std",
        "type": float,
        "help": "epsilon std for sampling latent noise",
    },
    {
        "name": "use_cp",
        "type": candle.str2bool,
        "default": False,
        "help": "checkpoint models with best val_loss",
    },
    # {'name':'shuffle',
    #'type': candle.str2bool,
    #'default': False,
    #'help':'shuffle data'},
    {
        "name": "use_tb",
        "type": candle.str2bool,
        "default": False,
        "help": "use tensorboard",
    },
    {
        "name": "tsne",
        "type": candle.str2bool,
        "default": False,
        "help": "generate tsne plot of the latent representation",
    },
]

required = [
    "activation",
    "batch_size",
    "dense",
    "dropout",
    "epochs",
    "initialization",
    "learning_rate",
    "loss",
    "optimizer",
    "rng_seed",
    "scaling",
    "latent_dim",
    "batch_normalization",
    "epsilon_std",
    "timeout",
]


class BenchmarkAdrp(candle.Benchmark):
    def set_locals(self):
        """Functionality to set variables specific for the benchmark
        - required: set of required parameters for the benchmark.
        - additional_definitions: list of dictionaries describing the additional parameters for the
        benchmark.
        """

        if required is not None:
            self.required = set(required)
        if additional_definitions is not None:
            self.additional_definitions = additional_definitions


def extension_from_parameters(params, framework=""):
    """Construct string for saving model with annotation of parameters"""
    ext = framework
    for i, n in enumerate(params["dense"]):
        if n:
            ext += ".D{}={}".format(i + 1, n)
    ext += ".A={}".format(params["activation"])
    ext += ".B={}".format(params["batch_size"])
    ext += ".E={}".format(params["epochs"])
    ext += ".L={}".format(params["latent_dim"])
    ext += ".LR={}".format(params["learning_rate"])
    ext += ".S={}".format(params["scaling"])

    if params["epsilon_std"] != 1.0:
        ext += ".EPS={}".format(params["epsilon_std"])
    if params["dropout"]:
        ext += ".DR={}".format(params["dropout"])
    if params["batch_normalization"]:
        ext += ".BN"
    if params["warmup_lr"]:
        ext += ".WU_LR"
    if params["reduce_lr"]:
        ext += ".Re_LR"
    if params["residual"]:
        ext += ".Res"

    return ext


def load_data(params, seed):

    # start change #
    if params["train_data"].endswith("csv") or params["train_data"].endswith("csv"):
        print("processing csv in file {}".format(params["train_data"]))

        url = params["data_url"]
        file_train = params["train_data"]
        train_file = candle.get_file(
            file_train, url + file_train, cache_subdir="Pilot1"
        )
        df = (pd.read_csv(train_file, skiprows=1).values).astype("float32")

        PL = df.shape[1]
        print("PL=", PL)

        PS = PL - 1

        df_y = df[:, 0].astype("float32")
        df_x = df[:, 1:PL].astype(np.float32)

        df_y.shape
        df_x.shape
        scaler = StandardScaler()
        df_x = scaler.fit_transform(df_x)

        X_train, X_test, Y_train, Y_test = train_test_split(
            df_x, df_y, test_size=0.20, random_state=42
        )
    else:
        print("expecting in file file suffix csv")
        sys.exit()

    return X_train, Y_train, X_test, Y_test, PS
