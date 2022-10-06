For finding meta-features that are proxy to certain errors follow the steps: 

1. pip install -r requirements.txt
2. python main.py (Collect all metrics with all errors applied -> Output in results/result.csv)
3. python ks_test.py (Find all unique error-metric combinations with Kolmogorov-Smirnov test -> Output in results/ks_output.csv)
4. python finding_mic.py (Find all unique error-metric combinations with MIC -> Output in results/unique_combinations_mic.csv)
