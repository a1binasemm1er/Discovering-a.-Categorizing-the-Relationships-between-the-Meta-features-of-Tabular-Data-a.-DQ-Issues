from asyncio.log import logger
from itertools import product
from pathlib import Path
import numpy as np
import pandas as pd
import os
import logging

from metrics import (
    Metric,
    Outliers,
    Completeness,
    MinSize,
    MinValueLength,
    SpecialCharsPattern,
    SoundexValue,
    Distinct,
    CapsPattern,
    SoundexMissingValues,
    DateStd,
    ValuePattern,
    KendallDistance
)

from generators import (
    ErrorGenerator,
    ExplicitMissingValues,
    ImplicitMissingValues,
    ExtraneousData,
    Duplicates,
    ReplaceSpecialCharacters,
    DeleteSpecialCharacters,
    SortFraction,
    LowerCase,
    ChangeDate,
    ErroneousData
)


class Validator:
    def __init__(self):
        self.metrics_for_numeric = ["completeness", "max", "min", "mean", "median", "mode", "std", "skewness", "percentile25", "percentile75", "max size", "min size", "avg size", "outliers", "distinct", "value pattern", "unsortedness", "kendall distance"]
        self.metrics_for_object = ["completeness", "max value length", "min value length", "avg value length", "special charachters pattern", "soundex", "distinct", "unsortedness", "caps pattern", "soundex missing values", "date std", "value pattern", "kendall distance"]
        self.metrics_for_bool = ["completeness"]
        self.errors_for_numeric = ["explicit missing values", "implicit missing values", "extraneous data", "duplicates", "erroneous data", "sort"]
        self.errors_for_object = ["misspell", "explicit missing values", "implicit missing values", "extraneous data", "duplicates", "replace special characters", "delete special characters", "sort", "lower case", "change date"]
        self.errors_for_bool = ["explicit missing values"]

    # metric matches column type?
    def check_metric(self, metric: Metric, col: pd.Series) -> bool:
        dtype = col.dtype
        return self.metric_matches_dtype(metric, dtype)

    def metric_matches_dtype(self, metric: Metric, dtype) -> bool: 
        if (metric.get_name() in self.metrics_for_numeric and pd.api.types.is_numeric_dtype(dtype) == True and (dtype != "bool")):
            return True
        elif (metric.get_name() in self.metrics_for_object and pd.api.types.is_object_dtype(dtype) == True):
            return True
        elif (metric.get_name() in self.metrics_for_bool and pd.api.types.is_bool_dtype(dtype) == True):
            return True
        else:
            return False

    # corruption matches column type? 
    def check_error(self, error: ErrorGenerator, col: pd.Series) -> bool:
        dtype = col.dtype
        return self.error_matches_dtype(error, dtype)
    
    def error_matches_dtype(self, error: ErrorGenerator, dtype) -> bool: 
        if (error.get_name() in self.errors_for_numeric and pd.api.types.is_numeric_dtype(dtype) == True):
            return True
        elif (error.get_name() in self.errors_for_object and pd.api.types.is_object_dtype(dtype) == True):
            return True
        elif (error.get_name() in self.errors_for_bool and pd.api.types.is_bool_dtype(dtype) == True):
            return True
        else:
            return False

class Suite:
    def __init__(self, config):
        self.config = config
        self.metrics = [
            Completeness(),
            Outliers(),            
            MinValueLength(),
            MinSize(),
            SpecialCharsPattern(),
            CapsPattern(),
            SoundexValue(),
            Distinct(),
            SoundexMissingValues(),
            ValuePattern(),
            DateStd(),
            KendallDistance()
        ]
        self.generators = [
            ExplicitMissingValues(),
            ImplicitMissingValues(),
            ExtraneousData(),
            Duplicates(),
            ReplaceSpecialCharacters(),
            DeleteSpecialCharacters(),
            SortFraction(),
            LowerCase(),
            ChangeDate(),
            ErroneousData()
        ]

    def run(self):
        logging.basicConfig(filename="suite.log", level = logging.INFO)
        data_folder = Path(self.config["folders"]["data"]) 
        fractions = np.arange(5, 100, 5)/100

        batch_number = 0

        if os.path.exists("results/result.csv"):
            os.remove("results/result.csv")
        else:
            logging.info("creating result.csv")
                
        validator = Validator()

        previously_computed_metrics = set()
        if os.path.exists("results/result.csv"):
            old_df = pd.read_csv("results/result.csv")
            previously_computed_metrics = set(old_df["metric name"].values)
            del old_df

        for f in data_folder.glob("*"):
            df = pd.read_csv(f, sep = ",")

            batch_result = pd.DataFrame()

            for (col, metric) in product(df.columns, self.metrics):

                # check if metrics were computed before
                if metric.get_name() in previously_computed_metrics:
                    continue

                # list of rows to write into batch_result
                rows = []

                if validator.check_metric(metric, df[col]) == True:
                    metric_value = metric.compute(df[col])
                    rows.append([f.name, batch_number, col, df[col].dtype, np.NaN, metric.get_name(), metric_value, np.NaN])

                for (error, fraction) in product(self.generators, fractions):

                    logging.info(f"batch: {batch_number}, column: {col}, metric: {metric.get_name()}, error: {error.get_name()}, fraction: {fraction}")

                    if validator.check_error(error, df[col]) == True:
                        corrupted_col = error.corrupt(df[col], fraction)

                        if validator.check_metric(metric, corrupted_col) == True:
                            metric_value = metric.compute(corrupted_col)
                            rows.append([f.name, batch_number, col, df[col].dtype, error.get_name(), metric.get_name(), metric_value, fraction])
                
                rows_df = pd.DataFrame(rows)
                batch_result = pd.concat([batch_result, rows_df]) 

            if not batch_result.empty: # no header between errors

                if batch_number == 0:
                    batch_result.to_csv("results/result.csv", mode = "a", header = ["batch name", "batch number", "column name", "column type", "error name", "metric name", "metric value", "fraction"], index=False)
                else:
                    batch_result.to_csv("results/result.csv", mode = "a", header = None, index = False)
            
            # get batch number
            batch_number += 1