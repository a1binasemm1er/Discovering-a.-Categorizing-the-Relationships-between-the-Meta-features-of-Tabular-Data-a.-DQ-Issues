import pandas as pd
import numpy as np
from abc import abstractmethod, ABC
from typing import Union
import scipy.stats as stats
from soundex import Soundex
import collections
import re

class Metric(ABC):
    @abstractmethod
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        ...
    def get_name(self):
        ...

class Max(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanmax(df)

    def get_name(self):
        return "max"

class Min(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanmin(df)
    
    def get_name(self):
        return "min"

class Mean(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanmean(df)
    
    def get_name(self):
        return "mean"

class Median(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanmedian(df)
    
    def get_name(self):
        return "median"

class Mode(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        m = stats.mode(df, nan_policy = 'omit')
        return m[0][0]
    
    def get_name(self):
        return "mode"

class Std(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanstd(df)
    
    def get_name(self):
        return "std"

class Percentile25(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanpercentile(df, 25)
    
    def get_name(self):
        return "percentile25"

class Percentile75(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return np.nanpercentile(df, 75)
    
    def get_name(self):
        return "percentile75"

class Completeness(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return 1. - np.sum(pd.isna(df)) / df.shape[0]
    
    def get_name(self):
        return "completeness"

class Skewness(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        return df.skew(axis = 0, skipna = True)
    
    def get_name(self):
        return "skewness"

class MaxSize(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        number_of_digits = []
        for value in df:
            if value is None:
                size = 0
            else: 
                size = len(str(abs(value)))
            number_of_digits.append(size)
        return max(number_of_digits)

    def get_name(self):
        return "max size"

class MinSize(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        number_of_digits = []
        for value in df:
            if np.isnan(value):
                size = 0
            else: 
                size = len(str(abs(value)))
            number_of_digits.append(size)
        return min(number_of_digits, default = 0)

    def get_name(self):
        return "min size"

class AvgSize(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        number_of_digits = []
        for value in df:
            if value is None:
                size = 0
            else: 
                size = len(str(abs(value)))
            number_of_digits.append(size)
        return sum(number_of_digits)/len(number_of_digits)

    def get_name(self):
        return "avg size"

class Outliers(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        q1 = np.nanpercentile(df, 25)
        q3 = np.nanpercentile(df, 75)
        iqr = q3 - q1
        lower_bound = q1 -(1.5 * iqr) 
        upper_bound = q3 +(1.5 * iqr)
        outliers_listed = []
        for value in df:
            if value < lower_bound or value > upper_bound:
                outliers_listed.append(str(value))
        outliers = "/ ".join(outliers_listed)
        if len(outliers_listed) == 0:
            return 0
        return max(outliers_listed)


    def get_name(self):
        return "outliers"

class MaxValueLength(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        number_of_chars = []
        for value in df:
            if value is np.NaN:
                size = 0
            else: 
                size = len(str(value))
            number_of_chars.append(size)
        return max(number_of_chars)

    def get_name(self):
        return "max value length"

class MinValueLength(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        number_of_chars = []
        for value in df:
            if value is np.NaN:
                size = 0
            else: 
                size = len(str(value))
            number_of_chars.append(size)
        return min(number_of_chars, default = 0)

    def get_name(self):
        return "min value length"

class AvgValueLength(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        number_of_chars = []
        for value in df:
            if value is np.NaN:
                size = 0
            else: 
                size = len(str(value))
            number_of_chars.append(size)
        return sum(number_of_chars)/len(number_of_chars)

    def get_name(self):
        return "avg value length"

class SpecialCharsPattern(Metric):
    """frequency of most frequent character to df size relationship"""
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        special_chars = ["-", "/", "@", "€", ":"]
        pattern = ""
        pattern_list = []
        most_freq_pattern = 0

        # find out the pattern, ignore NaN values and "None"s
        for value in df.dropna():
            count_special_chars = 0
            if value == "None":
                most_freq_pattern += 1
                continue
            pattern = ""
            for character in str(value):
                if character in special_chars:
                    pattern = pattern + character
                    count_special_chars += 1
                else:
                    pattern = pattern + "#"
            if count_special_chars == 0:
                continue
            pattern_list.append(pattern)
        # how frequent is the pattern?
        counter = collections.Counter(pattern_list)

        if len(counter.most_common(1)) == 0:
            return 1

        most_freq_pattern = most_freq_pattern + counter.most_common(1)[0][1]
        return most_freq_pattern/df.dropna().size

    def get_name(self):
        return "special charachters pattern"

class CapsPattern(Metric):
    """count capitals and lower case first letters and return it's relation"""
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        count_caps = 0
        count_smalls = 0

        for value in df.dropna():
            # ignore "None"s
            if value == "None":
                continue
            if str(value)[0].isupper():
                count_caps += 1
            if str(value).islower():
                count_smalls += 1
        if count_smalls == 0 or count_caps == 0:
            return 0
        return count_caps/count_smalls
    
    def get_name(self):
        return "caps pattern"

class ValuePattern(Metric):
    """frequency of number of words in value (for extraneous data)"""
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        words_number_list = []

        for value in df:
            words_number = str(value).split(" ")
            count_words = len(words_number)
            words_number_list.append(count_words)

        counter = collections.Counter(words_number_list)

        # frequency of most frequent value
        most_freq_pattern = counter.most_common(1)[0][1]
            
        return most_freq_pattern/df.size
    
    def get_name(self):
        return "value pattern"

class SoundexValue(Metric):
    """compare each df value's soundex code to the next, if they are equal - return 0. No duplicates - no 0s"""
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        sndx = Soundex()
        already_compared = set()
        
        for elem in df.tolist():
            if elem is np.NaN or str(elem) == "None" or str(elem) == "99999":
                continue

            elem_sndx = sndx.soundex(str(elem))

            if elem_sndx in already_compared:
                # duplicates present
                return 0
            already_compared.add(elem_sndx)
        
        # no duplicates
        return 1
    
    def get_name(self):
        return "soundex"

class SoundexMissingValues(Metric):
    """count soundex codes for None (N5) and return it's relation to number of rows"""
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        sndx = Soundex()
        count_none_entries = 0
        for value in df:
            if sndx.soundex(str(value)) == "N5":
                count_none_entries += 1
        return count_none_entries/df.size
    
    def get_name(self):
        return "soundex missing values"

class Distinct(Metric):
    """relation of number of unique entries to number of rows"""
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        # dropna for excluding the influence of missing values (explicit)
        if df.dropna().nunique() == df.dropna().size:
            return 0

        return df.dropna().nunique()/df.dropna().size

    def get_name(self):
        return "distinct"

class Unsortedness(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        new_df = df.copy()

        if pd.api.types.is_numeric_dtype(new_df.dtype) == True:
            new_df = new_df.replace(np.nan, 0)
        if pd.api.types.is_object_dtype(new_df.dtype) == True:
            new_df = new_df.replace(np.nan, "")
            new_df = new_df.replace("None", "")

        count_swaps = 0
        for elem in range(new_df.size):
            min_idx = elem

            for i in range(elem + 1, new_df.size):  

                try:
                    if new_df[i] < new_df[min_idx]:
                        min_idx = i
                except TypeError:
                    if str(new_df[i]) < str(new_df[min_idx]):
                        min_idx = i

            (new_df[elem], new_df[min_idx]) = (new_df[min_idx], new_df[elem])
            if elem != min_idx:
                count_swaps += 1
        
        return count_swaps/df.size
    
    def get_name(self):
        return "unsortedness"
    
class DateStd(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        date_pattern_yyyy = re.compile("[0-9]{4}[^0-9a-zA-Z][0-9]{1,2}[^0-9a-zA-Z][0-9]{1,2}$")
        date_pattern_dd =re.compile("^[0-9]{1,2}[^0-9a-zA-Z][0-9]{1,2}[^0-9a-zA-Z][0-9]{4}$")

        first_number_list = []

        for value in df:
            if value is np.NaN:
                continue
            if date_pattern_yyyy.match(str(value)) or date_pattern_dd.match(str(value)):
                sep = re.search("[^0-9]", value).group(0)
                first_number = int(re.split(sep, value)[0])                
                first_number_list.append(first_number)
        if not first_number_list:
            return 0
        return np.std(first_number_list)

    def get_name(self):
        return "date std"

class KendallDistance(Metric):
    def compute(self, df: Union[pd.DataFrame, pd.Series]):
        name = self.__class__.__name__
        assert isinstance(df, pd.Series), f"{name} is a single-column metric"

        try:
            sorted_sequence = df.sort_values(inplace = False)
        except TypeError:
            df = df.apply(str)
            sorted_sequence = df.sort_values(inplace = False)
        tau, _ = stats.kendalltau(sorted_sequence, df)

        if tau is np.NaN:
            return 1

        return tau
        

    def get_name(self):
        return "kendall distance"