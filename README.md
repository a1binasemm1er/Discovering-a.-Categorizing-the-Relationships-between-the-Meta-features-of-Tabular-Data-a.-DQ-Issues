For finding meta-features that are proxy to certain errors follow the steps: 

1. pip install -r requirements.txt
2. python main.py (Collect all metrics with all errors applied -> Output in results/result.csv -> log data in suite.log)
3. python ks_test.py (Find all unique error-metric combinations with Kolmogorov-Smirnov test -> Output in results/ks_output.csv -> log data in ks.log)
4. python finding_mic.py (Find all unique error-metric combinations with MIC -> Output in results/unique_combinations_mic.csv -> log data in mic.log)


python version 3.8.5
