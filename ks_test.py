import pandas as pd
import numpy as np
from itertools import product
from scipy import stats
import os

result = pd.read_csv("results/result.csv", sep = ",")

fractions = result["fraction"].dropna().unique().tolist()
metrics = result["metric name"].unique().tolist()
errors = result["error name"].dropna().unique().tolist()

if os.path.exists("results/ks_test.csv"):
    os.remove("results/ks_test.csv")

idx = 0

for fraction in fractions:
    for metric, error in product(metrics, errors):
        clean_values = result.loc[(result["metric name"] == metric) & (result["error name"].isnull())]["metric value"]
        dirty_values = result.loc[(result["metric name"] == metric) & (result["fraction"] == fraction) & (result["error name"] == error)]["metric value"]
        if len(dirty_values) == 0 or len(clean_values) == 0:
            continue
        p_value = stats.ks_2samp(clean_values, dirty_values)[1]
        if p_value < 0.05:
            data = []
            row = [fraction, metric, error]
            data.append(row) 
            df = pd.DataFrame(data = data)
        if idx == 0:
            df.to_csv("results/ks_test.csv", mode = "a", header = ["fraction", "metric", "error"], index = False)
        else:
            df.to_csv("results/ks_test.csv", header = None, mode = "a", index = False) 
        
        idx += 1


ks_result = pd.read_csv("results/ks_test.csv", sep = ",")
df_result = ks_result.groupby([col for col in ks_result.columns if col != "fraction"]).min().reset_index()

df_result.to_csv("results/ks_output.csv", sep = ",")