


# Documentation

## Data

### Download data - `download_data.sh`

To download data run in shell:
```shell
bash scripts/data/download_data.sh
```
The script will
- download data from uniprot databases
- create folder data/raw (You can change it in script `params` section)
- extract fasta files in data/raw 
- rebane files to names (You can change it in script `params` section)
- print what amount of sequences is in each files

### Normalize files - `normalize_fasta`

To normalize downloaded run in shell:
```shell
python3 scripts/data/normalize_fasta.py -i data/raw/* -o data/merged_processed 
```
The script:
- take file/files `-i` 
- join sequences parts to one line (fasta format) with
    - removing duplicates (comparing sequences)
    - Cutting sequences to given length (`-l` parameter by default = 2500)
- create output folder - `-o` argument
- return normalized sequences in given folder `-o` with `_flat` suffix 


### Split files - `split_fasta.py`

To split data run in shell:
```shell
python3 scripts/data/split_fasta.py -i data/merged_processed/* data/splitted/
```
The script:
- takes file/files
- each file is splitted into $n$ sequences (`--split_n`) 
- `--test_n` is parameter for test size split, by default is set to `None` and takes:  (to use empty files) 

# Commands run history

## Datasets

### Download data:
```shell
# proteins for prediction
bash scripts/data/download_data.sh
# Disorderded data
wget https://www.mimuw.edu.pl/~lukaskoz/teaching/adp/labs/lab_hpc3/DisProt_human_fragments_flat.csv 
```

### Normalize data:
```shell
python3 scripts/data/normalize_fasta.py -i data/raw/* -o data/merged_processed 
```

### Split data:
```shell
python3 scripts/data/split_fasta.py -i data/merged_processed/* data/splitted/
```

> Remark: Here i splitted data in different manner:
> $$ \mathrm{all_sequences} \mathrm{mod} \mathmrm{`--split_n`}$$



## Computational Performance & predictions

### IUpred

#### Computational Performance: estimation 

To run predictions i used:

```shell
srun --partition=common --cpus-per-task=1 --mem=2000 --time=00:30:00 --pty $SHELL
```

```shell
# E_coli
## Obtain estimation - short
bash scripts/helpers/run_on_ram.sh scripts/wrappers/IUpred_wrapper.py data/splitted/E_coli/E_coli_test.fasta data/results/IUpred/short/E_coli /dev/shm --exec_mode short --mode test --stats_path stats.csv
## obtain estimation - long
bash scripts/helpers/run_on_ram.sh scripts/wrappers/IUpred_wrapper.py data/splitted/E_coli/E_coli_test.fasta data/results/IUpred/long/E_coli /dev/shm --exec_mode long --mode test --stats_path stats.csv

## Obtain stats - short
python3 scripts/analysis/summarize_test_stats.py -i data/results/IUpred/short/E_coli/stats.csv -s report/results/time_estimation_iupred_E_coli_short.csv
## Obtain stats - long 
python3 scripts/analysis/summarize_test_stats.py -i data/results/IUpred/long/E_coli/stats.csv -s report/results/time_estimation_iupred_E_coli_long.csv

```

```shell
# H_sapiens
## Obtain estimation - short
bash scripts/helpers/run_on_ram.sh scripts/wrappers/IUpred_wrapper.py data/splitted/H_sapiens/H_sapiens_test.fasta data/results/IUpred/short/H_sapiens /dev/shm --exec_mode short --mode test --stats_path stats.csv
## obtain estimation - long
bash scripts/helpers/run_on_ram.sh scripts/wrappers/IUpred_wrapper.py data/splitted/H_sapiens/H_sapiens_test.fasta data/results/IUpred/long/H_sapiens /dev/shm --exec_mode long --mode test --stats_path stats.csv

## Obtain stats - short
python3 scripts/analysis/summarize_test_stats.py -i data/results/IUpred/short/H_sapiens/stats.csv -s report/results/time_estimation_iupred_H_sapiens_short.csv
## Obtain stats - long 
python3 scripts/analysis/summarize_test_stats.py -i data/results/IUpred/long/H_sapiens/stats.csv -s report/results/time_estimation_iupred_H_sapiens_long.csv
```

```shell
# SwissProt
## Obtain estimation - short
bash scripts/helpers/run_on_ram.sh scripts/wrappers/IUpred_wrapper.py data/splitted/SwissProt/SwissProt_test.fasta data/results/IUpred/short/SwissProt /dev/shm --exec_mode short --mode test --stats_path stats.csv
## obtain estimation - long
bash scripts/helpers/run_on_ram.sh scripts/wrappers/IUpred_wrapper.py data/splitted/SwissProt/SwissProt_test.fasta data/results/IUpred/long/SwissProt /dev/shm --exec_mode long --mode test --stats_path stats.csv

## Obtain stats - short
python3 scripts/analysis/summarize_test_stats.py -i data/results/IUpred/short/SwissProt/stats.csv -s report/results/time_estimation_iupred_SwissProt_short.csv
## Obtain stats - long 
python3 scripts/analysis/summarize_test_stats.py -i data/results/IUpred/long/SwissProt/stats.csv -s report/results/time_estimation_iupred_SwissProt_long.csv
```

#### Predictions - run all parts

```shell
# short
nohup bash scripts/helpers/launch_all_IUPRED_short.sh > logs/iupred/short/all 2>&1 &
# long 
nohup bash scripts/helpers/launch_all_IUPRED_long.sh > logs/iupred/long/all 2>&1 &
```

#### Merge results

```shell
# E_coli
## short
cat data/results/IUpred/short/E_coli/*_pred.fasta > data/results_merged/E_coli/iupred_short.fasta

# long
cat data/results/IUpred/long/E_coli/*_pred.fasta > data/results_merged/E_coli/iupred_long.fasta

# H_sapiens
## short
cat data/results/IUpred/short/H_sapiens/*_pred.fasta > data/results_merged/H_sapiens/iupred_short.fasta

# long
cat data/results/IUpred/long/H_sapiens/*_pred.fasta > data/results_merged/H_sapiens/iupred_long.fasta

# SwissProt
## short
cat data/results/IUpred/short/SwissProt/*_pred.fasta > data/results_merged/SwissProt/iupred_short.fasta

# SwissProt
cat data/results/IUpred/long/SwissProt/*_pred.fasta > data/results_merged/SwissProt/iupred_long.fasta
```


### ProtBert

#### Computational Performance: estimation - cpu


i downloaded model_bert, becuase i did not have access to  /home/lukaskoz/

```shell
# E_coli
## Obtain estimation
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/E_coli/E_coli_test.fasta data/results/ProtBert/E_coli /dev/shm --mode test --stats_path cpu_stats.csv --device -1
```

```bash
# H_sapiens
## Obtain estimation
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/H_sapiens/H_sapiens_test.fasta data/results/ProtBert/H_sapiens /dev/shm --mode test --stats_path cpu_stats.csv --device -1
```

> Here we do not calculated in proper time and srun was dropped - skipped because have results from two othres

```bash
# SwissProt
## Obtain estimation
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/SwissProt/SwissProt_test.fasta data/results/ProtBert/SwissProt /dev/shm --mode test --stats_path cpu_stats.csv --device -1
```

#### Computational Performance: estimation  gpu

```shell
# E_coli
## Obtain estimation - cpu
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/E_coli/E_coli_test.fasta data/results/ProtBert/E_coli /dev/shm --mode test --stats_path gpu_stats.csv --device -1

## Obtain estimation - gpu
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/E_coli/E_coli_test.fasta data/results/ProtBert/E_coli /dev/shm --mode test --stats_path gpu_stats.csv --device 0

## Obtain stats - cpu
python3 scripts/analysis/summarize_test_stats.py -i data/results/ProtBert/E_coli/cpu_stats.csv -s report/results/cost_estimation/time_estimation_ProtBert_E_coli_cpu.csv

## Obtain stats - gpu
python3 scripts/analysis/summarize_test_stats.py -i data/results/ProtBert/E_coli/gpu_stats.csv -s report/results/cost_estimation/time_estimation_ProtBert_E_coli_gpu.csv
```

```bash
# H_sapiens

## Obtain estimation - cpu - NONE 

## Obtain estimation - gpu
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/H_sapiens/H_sapiens_test.fasta data/results/ProtBert/H_sapiens /dev/shm --mode test --stats_path gpu_stats.csv --device 0

## Obtain stats - cpu - NONE 

## Obtain stats - gpu
python3 scripts/analysis/summarize_test_stats.py -i data/results/ProtBert/H_sapiens/gpu_stats.csv -s report/results/cost_estimation/time_estimation_ProtBert_H_sapiens_gpu.csv
```

```bash
# SwissProt
## Obtain estimation - cpu
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/SwissProt/SwissProt_test.fasta data/results/ProtBert/SwissProt /dev/shm --mode test --stats_path gpu_stats.csv --device -1
## Obtain estimation - gpu
bash ./scripts/helpers/run_on_ram.sh scripts/wrappers/ProtBert_wrapper.py data/splitted/SwissProt/SwissProt_test.fasta data/results/ProtBert/SwissProt /dev/shm --mode test --stats_path gpu_stats.csv --device 0

## Obtain stats - cpu
python3 scripts/analysis/summarize_test_stats.py -i data/results/ProtBert/SwissProt/cpu_stats.csv -s report/results/cost_estimation/time_estimation_ProtBert_SwissProt_cpu.csv

## Obtain stats - gpu
python3 scripts/analysis/summarize_test_stats.py -i data/results/ProtBert/SwissProt/gpu_stats.csv -s report/results/cost_estimation/time_estimation_ProtBert_SwissProt_gpu.csv
```

#### Predictions - run all parts

```shell
nohup bash scripts/helpers/launch_all_ProtBert.sh > logs/ProtBert/all 2>&1 &
```

#### Merge results

```shell
# E_coli
cat data/results/ProtBert/E_coli/*_pred.fasta > data/results_merged/E_coli/ProtBert.fasta

# H_sapiens
cat data/results/ProtBert/H_sapiens/*_pred.fasta > data/results_merged/H_sapiens/ProtBert.fasta

# SwissProt
cat data/results/ProtBert/SwissProt/*_pred.fasta > data/results_merged/SwissProt/ProtBert.fasta
```

## Analysis 

Here are scripts used for creating analysis

### Resource Scaling and Intuition


#### Time estimation results

Script for mergind time estimations
```shell
python3 scripts/analysis/summarize_test_stats_merge.py -i report/results/cost_estimation/ -o report/results/time_estimation_merged.csvsh
```

#### Total Execution Time

To find whole time i used times of start and end of certain jobs, which ids i had in my logs. 

```shell
# short

## E.Coli
START=$(sacct -j 170230 --format=Start -n -P | head -n 1); \
END=$(sacct -j 170233 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"

## H.Sapiens
START=$(sacct -j 170234 --format=Start -n -P | head -n 1); \
END=$(sacct -j 170255 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"

## Swissprot
START=$(sacct -j 170256 --format=Start -n -P | head -n 1); \
END=$(sacct -j 171301 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"
```

```shell
# Long

## E.Coli
START=$(sacct -j 170262 --format=Start -n -P | head -n 1); \
END=$(sacct -j 170309 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"

## H.Sapiens
START=$(sacct -j 170311 --format=Start -n -P | head -n 1); \
END=$(sacct -j 171330 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"

## Swissprot
START=$(sacct -j 170256 --format=Start -n -P | head -n 1); \
END=$(sacct -j 171301 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"
```

```shell
# ProtBert

## E.Coli
START=$(sacct -j 169642 --format=Start -n -P | head -n 1); \
END=$(sacct -j 169670 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"

## H.Sapiens
START=$(sacct -j 169671 --format=Start -n -P | head -n 1); \
END=$(sacct -j 170217 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"

## Swissprot
START=$(sacct -j 170256 --format=Start -n -P | head -n 1); \
END=$(sacct -j 171301 --format=End -n -P | head -n 1); \
echo "Start: $START"; \
echo "End: $END"; \
echo "Whole time: $(python3 -c "from datetime import datetime; s=datetime.fromisoformat('$START'); e=datetime.fromisoformat('$END'); print(e-s)")"
```

#### Percentage of disorder 

```shell
# IUPred
## E.Coli
### Short
python3 scripts/analysis/calculate_disorder_pct.py data/results_merged/E_coli/iupred_short.fasta report/results/structure_pct/E_coli_iupred_short.csv
### Long
python3 scripts/analysis/calculate_disorder_pct.py data/results_merged/E_coli/iupred_long.fasta report/results/structure_pct/E_coli_iupred_long.csv

## H.Sapiens
### Short
python3 scripts/analysis/calculate_disorder_pct.py data/results_merged/H_sapiens/iupred_short.fasta report/results/structure_pct/H_sapiens_iupred_short.csv
### Long
python3 scripts/analysis/calculate_disorder_pct.py data/results_merged/H_sapiens/iupred_long.fasta report/results/structure_pct/H_sapiens_iupred_long.csv

## SwissProt
### Short
python3 scripts/analysis/calculate_disorder_pct.py data/results_merged/SwissProt/iupred_short.fasta report/results/structure_pct/SwissProt_iupred_short.csv
### Long
python3 scripts/analysis/calculate_disorder_pct.py data/results_merged/SwissProt/iupred_long.fasta report/results/structure_pct/SwissProt_iupred_long.csv
````

```shell
# ProtBert ss
## E.Coli
python3 scripts/analysis/calculate_ss_pct.py data/results_merged/E_coli/ProtBert.fasta report/results/structure_pct/E_coli_ss.csv
## H.Sapiens
python3 scripts/analysis/calculate_ss_pct.py data/results_merged/H_sapiens/ProtBert.fasta report/results/structure_pct/H_sapiens_ss.csv
## SwissProt
python3 scripts/analysis/calculate_ss_pct.py data/results_merged/SwissProt/ProtBert.fasta report/results/structure_pct/SwissProt_ss.csv
```

```shell
# merge results
python3 scripts/analysis/pct_merge.py -i report/results/structure_pct/ -o report/results/
```

#### Model Validation against DisProt

```shell
# short sequences
python3 scripts/analysis/calculate_mcc.py data/results_merged/H_sapiens/iupred_short.fasta data/raw/DisProt_human_fragments_flat.csv
# long sequences
python3  scripts/analysis/calculate_mcc.py data/results_merged/H_sapiens/iupred_long.fasta data/raw/DisProt_human_fragments_flat.csv
```

#### Identification of Functional Transitions

```shell
# short sequences
python3 scripts/analysis/filter_induced_disorder.py data/results_merged/H_sapiens/iupred_short.fasta data/results_merged/H_sapiens/ProtBert.fasta 5000 40 20 1 > data/results_merged/H_sapiens/H_sapiens_Induced_short_top5000.fasta
# long sequences
python3 scripts/analysis/filter_induced_disorder.py data/results_merged/H_sapiens/iupred_long.fasta data/results_merged/H_sapiens/ProtBert.fasta 5000 40 20 1 > data/results_merged/H_sapiens/H_sapiens_Induced_long_top5000.fasta
```

#### Discovery of Helical Scaffolds

```shell
# it hadles both long and short
python3 scripts/analysisfilter_ss.py data/results_merged/SwissProt/ProtBert.fasta 5000 100 60 20 2 -1 -2 1 > data/results_merged/SwissProt/SwissProt_SHS_top5000.fasta
```



