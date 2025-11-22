from pathlib import Path

import pandas as pd
import numpy as np
from scipy import stats

from taptracker.connections import model_get_inputs


def process(key_file: str | Path) -> dict:
    df = pd.read_csv(key_file).query("hand != 'U'")

    input_cols = model_get_inputs()

    # Create percentile functions ot use for aggregates
    def percentn(n):
        return lambda x: np.percentile(x, n)

    percent_funcs = [percentn(n) for n in range(10, 100, 10)]

    agg_df = keysprep(
        df,
        ["FlightTime", "HoldTime"],
        [
            np.mean,
            np.std,
            stats.kurtosis,
            stats.skew,
            *percent_funcs
        ],
        input_cols,
    )

    payload_inner = []
    for col, values_dict in agg_df.to_dict().items():
        for value in values_dict.values():
            value = 1 if col == "id" else value
            payload_inner.append({"name": col, "value": value})

    return {"inputs": payload_inner}


def keysprep(user_file_df, columns_to_aggregate, aggregation_functions, scorecols):
    """
    :param user_file_df: pandas dataframe containing all the raw data, one line per keystroke.
    :param columns_to_aggregate: list of columns that we wish to calculate summary statistics from
    :param aggregation_functions: list of function to be applied on each column (example: np.mean or np.std)
    :return: a dataframe with 1 row per user, with requested summary statistics as columns, calculated individually for
             left/right/LL/LR/RR/RL keystrokes
    """
    # assert all([col in user_file_df.columns for col in ["ID", "Hand", "Direction"]])
    user_file_df.rename(
        columns={"id": "ID", "hand": "Hand", "key": "Key", "hold_time": "HoldTime"},
        inplace=True,
    )
    user_file_df["FlightTime"] = user_file_df["press_ts"] - user_file_df[
        "release_ts"
    ].shift(+1)

    # Parse hand and direction by pressed key
    user_file_df["Direction"] = user_file_df["Hand"] + user_file_df["Hand"].shift(+1)
    user_file_df.drop(
        user_file_df.index[0], inplace=True
    )  # Because first row cannot have a valid direction

    # Calculate statistics for rows that match 'Left' / 'Right' keystrokes:
    left_right_stats = (
        user_file_df.groupby(["ID", "Hand"])[columns_to_aggregate]
        .agg(aggregation_functions)
        .reset_index()
    )
    leftHandStats = left_right_stats[left_right_stats.Hand == "L"]
    rightHandStats = left_right_stats[left_right_stats.Hand == "R"]
    leftHandStats.columns = [
        "L_" + col + "_" + stat if col not in ("ID", "Hand") else col
        for col, stat in leftHandStats.columns
    ]
    rightHandStats.columns = [
        "R_" + col + "_" + stat if col not in ("ID", "Hand") else col
        for col, stat in rightHandStats.columns
    ]

    # Calculate statistics for rows that match 'LR'/'RR'/'RL'/'LL' keystrokes:
    lr_rl_ll_rr_stats = (
        user_file_df.groupby(["ID", "Direction"])[columns_to_aggregate]
        .agg(aggregation_functions)
        .reset_index()
    )
    ll_stats = lr_rl_ll_rr_stats[lr_rl_ll_rr_stats.Direction == "LL"].drop("Direction", axis=1)
    ll_stats.columns = [
        "LL_" + col + "_" + stat if col not in ("ID", "Direction") else col
        for col, stat in ll_stats.columns
    ]
    lr_stats = lr_rl_ll_rr_stats[lr_rl_ll_rr_stats.Direction == "LR"].drop("Direction", axis=1)
    lr_stats.columns = [
        "LR_" + col + "_" + stat if col not in ("ID", "Direction") else col
        for col, stat in lr_stats.columns
    ]
    rl_stats = lr_rl_ll_rr_stats[lr_rl_ll_rr_stats.Direction == "RL"].drop("Direction", axis=1)
    rl_stats.columns = [
        "RL_" + col + "_" + stat if col not in ("ID", "Direction") else col
        for col, stat in rl_stats.columns
    ]
    rr_stats = lr_rl_ll_rr_stats[lr_rl_ll_rr_stats.Direction == "RR"].drop("Direction", axis=1)
    rr_stats.columns = [
        "RR_" + col + "_" + stat if col not in ("ID", "Direction") else col
        for col, stat in rr_stats.columns
    ]

    # Join all dfs together:
    res = (
        leftHandStats.merge(rightHandStats, on="ID", how="outer")
        .merge(ll_stats, on="ID", how="outer")
        .merge(lr_stats, on="ID", how="outer")
        .merge(rl_stats, on="ID", how="outer")
        .merge(rr_stats, on="ID", how="outer")
    )

    # Check if any users were lost during the aggregation process:
    if len(set(res.ID.values)) < len(set(user_file_df.ID.values)):
        s = set(user_file_df.ID.values)
        lost = [u for u in s if u not in res.ID.values]
        print("lost {} unique IDS in the aggregation process: ".format(len(lost)), lost)

    res.set_index("ID")
    cols = set(res.columns.values.copy())
    for col in cols:
        if col.startswith("Hand") or col.startswith("Direction"):
            res = res.drop(col, axis=1)

    res.columns = res.columns.str.lower()
    return res[scorecols]
