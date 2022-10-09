This is the code based solution for a bachelor thesis "Discovering and Categorizing the Relationships between the Meta-features of Tabular Data and Data Quality Issues"
Technische Universität Berlin
Chair of Database Systems and Information Management
Author: Albina Semmler
Advisor: Sergey Redyuk


For finding meta-features that are proxy to certain errors follow the steps: 

0. Make sure you have python version 3.8.5
1. Install dependencies 
      pip install -r requirements.txt
      
2. Collect all metrics with all errors applied
      python main.py
   Output file is in results/result.csv
   Log data is in suite.log
   
3. Find all unique error-metric combinations with Kolmogorov-Smirnov test
      python ks_test.py   
   Output is in results/ks_output.csv
   Log data is in ks.log
   
4. Find all unique error-metric combinations with MIC
      python finding_mic.py
   Output is in results/unique_combinations_mic.csv
   Log data is in mic.log
