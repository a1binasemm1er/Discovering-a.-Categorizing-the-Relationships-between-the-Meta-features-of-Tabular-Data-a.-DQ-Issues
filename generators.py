import pandas as pd
import numpy as np
import random
from abc import abstractmethod, ABC
from typing import Union
import re

class ErrorGenerator(ABC):
    @abstractmethod
    def corrupt(self, df: Union[pd.DataFrame, pd.Series]):
        ...
    def get_name(self):
        ...

class ExplicitMissingValues(ErrorGenerator):
    """replace random values with None"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False) # False -> no sampling on the same row twice
        new_df = df.copy()
        
        for i, _ in random_subset.items():
            new_df.loc[i] = np.NaN # locate all entries by index i and set them on None
        
        return new_df

    def get_name(self):
        return "explicit missing values"


class ImplicitMissingValues(ErrorGenerator):
    """replace random values with string None (for object type values) or number 99999 (for numeric type values) """

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False) # False -> no sampling on the same row twice
        new_df = df.copy()
        
        for i, _ in random_subset.items():
            if pd.api.types.is_object_dtype(df.dtype) == True:
                new_df.loc[i] = "None"
            if pd.api.types.is_numeric_dtype(df.dtype) == True:
                new_df.loc[i] = 99999
        
        return new_df

    def get_name(self):
        return "implicit missing values"

class ExtraneousData(ErrorGenerator):
    """randomly choose element from qwerty and add it to value"""

    def __init__(self):
        self.qwerty = [
            "fsfsdfsf",
            "sdf gsfh fgjf",
            "dfgdf gdfgd",
            "hnhklköjkhkg",
            "lj dfks knb",
            "hklhkh",
            "lpujhf",
            "fadsdvb",
            "65767",
            "365 lkh",
            "0897899",
            "24254",
            "7878089",
            "2235435",
            "fgkjhvb kjk",
            "879izukhj",
            "23 4edg",
            "768",
            "576897gh"
        ]

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()
        
        for i, _ in random_subset.items():
            new_df.loc[i] = str(new_df.loc[i]) + " " + random.choice(self.qwerty)

        return new_df

    def get_name(self):
        return "extraneous data"

class Duplicates(ErrorGenerator):
    """duplicate random value and write it instead next value"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()

        for i, _ in random_subset.items():
            if new_df.loc[i] != new_df.iloc[-1]: # not for the last row
                new_df.loc[i+1] = new_df.loc[i]
        
        return new_df

    def get_name(self):
        return "duplicates"


class ReplaceSpecialCharacters(ErrorGenerator):
    """replace special character with another one"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()
        spec_char = ["-", "/", ":"]

        for i, _ in random_subset.items():
            if new_df.loc[i] is np.NaN:
                continue
            sep_tuple = re.search("[^0-9a-zA-Z]", new_df.loc[i])
            if sep_tuple is not None:
                sep = sep_tuple.group(0)
                if sep in spec_char:
                    spec_char_copy = spec_char.copy()
                    spec_char_copy.remove(sep)
                    new_df.loc[i] = new_df.loc[i].replace(sep, random.choice(spec_char_copy))
        
        return new_df

    def get_name(self):
        return "replace special characters"


class LowerCase(ErrorGenerator):
    """lower all letters in string"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()

        for i, _ in random_subset.items():
            value = new_df.loc[i]
            if value is not np.NaN and isinstance(value, str):
                new_df.loc[i] = new_df.loc[i].lower()

        return new_df
    
    def get_name(self):
        return "lower case"

class DeleteSpecialCharacters(ErrorGenerator):
    """delete special character as if it was missed"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()
        old_chars = ["-", "/", "@", "€", ":"]
        new_char = ""

        # if df.name == "Date":
            # return new_df

        for i, _ in random_subset.items():
            value = new_df.loc[i]
            for old_char in old_chars:
                if old_char in str(value):
                    new_df.loc[i] = new_df.loc[i].replace(old_char, new_char)
        
        return new_df

    def get_name(self):
        return "delete special characters"

class SortFraction(ErrorGenerator):
    """sort first *fraction value* values in series"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        new_df = df.copy().dropna()
        to_sort = new_df.size * fraction
        sorted = new_df.head(int(to_sort)).sort_values()
        new_df[0:int(to_sort)] = sorted

        return new_df

    def get_name(self):
        return "sort"

class ChangeDate(ErrorGenerator):

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()

        date = re.compile("[0-9]+[^0-9a-zA-Z][0-9]+[^0-9a-zA-Z][0-9]+") # date/date/date or date-date-date or date.date.date or ...
        year_first = re.compile("[0-9]{4}[^0-9a-zA-Z][0-9]{1,2}[^0-9a-zA-Z][0-9]{1,2}$") # yyyy/...
        year_last = re.compile("^[0-9]{1,2}[^0-9a-zA-Z][0-9]{1,2}[^0-9a-zA-Z][0-9]{4}") # .../yyyy

        for i, _ in random_subset.items():
            if new_df.loc[i] is np.NaN:
                continue
            if date.match(str(new_df.loc[i])):
                # find separator
                sep = re.search("[^0-9]", new_df.loc[i]).group(0)
                date_list = new_df.loc[i].split(sep)
                if year_first.match(str(new_df.loc[i])):
                    new_df.loc[i] = (f"{date_list[1]}{sep}{date_list[2]}{sep}{date_list[0]}")
                elif year_last.match(str(new_df.loc[i])):
                    new_df.loc[i] = (f"{date_list[2]}{sep}{date_list[0]}{sep}{date_list[1]}")
        
        return new_df
    
    def get_name(self):
        return "change date"

class ErroneousData(ErrorGenerator):
    """replace with value much bigger then max in series"""

    def corrupt(self, df: Union[pd.DataFrame, pd.Series], fraction: float):

        random_subset = df.sample(frac = fraction, replace = False)
        new_df = df.copy()

        for i, _ in random_subset.items():
            new_df.loc[i] = new_df.loc[i] * 100

        return new_df
    
    def get_name(self):
        return "erroneous data"