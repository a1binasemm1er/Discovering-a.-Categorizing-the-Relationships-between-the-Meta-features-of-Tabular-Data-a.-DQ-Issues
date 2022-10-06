import pandas as pd
import numpy as np
from itertools import product
from minepy import MINE
from scipy.stats import variation
import os


class MetricName:
    completeness = "completeness"
    outliers = "outliers"      
    min_length = "min value length"
    min_size = "min size"
    spec_char = "special charachters pattern"
    caps = "caps pattern"
    soundex_dupl = "soundex"
    dist = "distinct"
    sound_miss_val = "soundex missing values"
    value_pattern = "value pattern"
    date = "date std"
    tau = "kendall distance"
class ErrorName:
    explicit_missing_values = "explicit missing values"
    implicit_missing_values = "implicit missing values"
    extr_data = "extraneous data"
    dupl = "duplicates"
    repl_chars = "replace special characters"
    del_chars = "delete special characters"
    sort = "sort"
    lower = "lower case"
    date = "change date"
    err_data = "erroneous data"

output = pd.read_csv("results/result.csv", sep = ",")
fractions = np.arange(0, 100, 5)/100
metrics = [
    MetricName.completeness, 
    MetricName.outliers, 
    MetricName.min_length, 
    MetricName.min_size, 
    MetricName.spec_char, 
    MetricName.caps, 
    MetricName.soundex_dupl, 
    MetricName.dist, 
    MetricName.sound_miss_val, 
    MetricName.value_pattern,
    MetricName.date, 
    MetricName.tau
]
errors = [
    ErrorName.explicit_missing_values, 
    ErrorName.implicit_missing_values, 
    ErrorName.extr_data, 
    ErrorName.dupl, 
    ErrorName.repl_chars, 
    ErrorName.del_chars, 
    ErrorName.sort, 
    ErrorName.lower, 
    ErrorName.date, 
    ErrorName.err_data
]
batches = output["batch number"].unique().tolist()
columns = output["column name"].unique().tolist()

if os.path.exists("results/all_metric_error_mic.csv"):
    os.remove("results/all_metric_error_mic.csv")

idx = 0

for metric, error, column, batch in product(metrics, errors, columns, batches):
    row_to_write = []
    
    clean = output.loc[(output["error name"].isnull()) & (output["metric name"] == metric)]
    error_metric = output.loc[(output["error name"] == error) & (output["metric name"] == metric)]
    
    column_name = error_metric.loc[error_metric["column name"] == column]
    clean = clean.loc[clean["column name"] == column]
    
    batch_number = column_name.loc[column_name["batch number"] == batch]
    clean = clean.loc[clean["batch number"] == batch]
    clean = clean["metric value"].tolist()
    # extraneous data problem with column type
    if len(clean) == 0:
        continue
    # if error isn't applicable on metric
    if batch_number.shape[0] == 0:
        continue
    column_type = batch_number["column type"].unique().tolist()[0]
    column_name = batch_number["column name"].unique().tolist()[0]

    metric_value = batch_number["metric value"].tolist()
    mine = MINE(est="mic_approx")
    mine.compute_score((clean + metric_value), fractions)
    row = [metric, error, column_name, column_type, mine.mic()]
    row_to_write.append(row)
    df = pd.DataFrame(row_to_write)
    if idx == 0:
        df.to_csv("results/all_metric_error_mic.csv", mode = "a", header = ["metric", "error", "column", "type", "mic"], index = False)
    else:
       df.to_csv("results/all_metric_error_mic.csv", header = None, mode = "a", index = False) 

    idx += 1

### find unique combinations 
if os.path.exists("results/unique_combinations_mic.csv"):
    os.remove("results/unique_combinations_mic.csv")

output = pd.read_csv("results/all_metric_error_mic.csv", sep = ",")
metrics = output["metric"].unique().tolist()
errors = output["error"].unique().tolist()
columns = output["column"].unique().tolist()

for metric, error, column in product(metrics, errors, columns):
    row_to_write = []
    mic = output.loc[(output["metric"] == metric) & (output["error"] == error) & (output["column"] == column)]["mic"]
    if variation(mic) < 0.2:
        row = [metric, error]
        row_to_write.append(row)
        df = pd.DataFrame(row_to_write)
        df.to_csv("results/var_metric_error_mic.csv", mode = "a", header = None, index = False)

metric_error_mic = pd.read_csv("results/var_metric_error_mic.csv", sep = ",")
already_compared = []
for _, row in metric_error_mic.iterrows():
    if row.tolist() in already_compared:
        continue
    else:
        already_compared.append(row.tolist())

rows = []
for comb in already_compared:
    rows.append(comb)
df_combination = pd.DataFrame(rows)
df_combination.to_csv("results/unique_combinations_mic.csv", mode = "a", header = None, index = False)






