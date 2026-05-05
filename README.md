# ADP project:  High-Performance Computing

## Introduction
This project was developed as part of the **Architecture of Large Projects in Bioinformatics (ADP)** course. The primary objective was to design and implement High-Performance Computing (HPC) workflows on a remote server, effectively balancing **CPU** and **GPU** resources. 

Project focused on:
*   Comparing protein disorder patterns across different proteomes using IUPred.
*   Predicting secondary structure propensities using the ProtBert transformer model.
*   Performing large-scale data mining on model organisms (*E. coli*, *H. sapiens*) and the comprehensive SwissProt database.

## Documentation and Results
Final conclusion and workflow is contained in following files:
*   **[report.md](report_refined.md)** – The final report containing all analysis, tables, and protein visualizations.
*   **[SCRIPTS_RUN_HISTORY.md](SCRIPTS_RUN_HISTORY.md)** – A full audit trail. It contains every command executed, including specific file paths and environment parameters.

## HPC Strategy and Optimization
To maximize computational throughput and maintain cluster stability, the following technical workflow was implemented:

*   **Data Partitioning (Splitting)**: Large proteome datasets were segmented into smaller packages to enable parallel processing and prevent Out-of-Memory (OOM) errors during inference

*   **RAM-Disk Execution (`/dev/shm`)**: Each data chunk was transferred to the local RAM disk before execution to utilize high-speed memory access and eliminate disk I/O bottlenecks.

*   **Batch Processing**: Slurm scripts managed the processing of data packages in automated batches, ensuring optimal GPU/CPU occupancy while preventing filesystem overloading

---

## Script Overview

To help navigation, the scripts are categorized by their role in the pipeline, as well as all scripts runs are in [SCRIPTS_RUN_HISTORY.md](SCRIPTS_RUN_HISTORY.md):


### 1. Data Preparation
*   `scripts/data/download_data.sh` – Automates the retrieval of raw datasets from UniProt and DisProt.
*   `scripts/data/normalize_fasta.py` – Standardizes FASTA headers, removes duplicates, and filters sequences by length.
*   `scripts/data/split_fasta.py` – Segments  datasets into parts with given sequences amount. 

### 2. Execution Wrappers and Helpers
*   `scripts/wrappers/IUpred_wrapper.py` – Manages the execution of disorder predictions.
*   `scripts/wrappers/ProtBert_wrapper.py` – Handles model loading and inference for secondary structure on either CPU or GPU.
*   `scripts/helpers/run_on_ram.sh` – A utility script to handle data transfer to RAM `/dev/shm.  

### 3. Analysis and Statistics
*   `scripts/analysis/calculate_disorder_pct.py` – Computes global disorder percentages for processed files.
*   `scripts/analysis/calculate_ss_pct.py` – Calculates the distribution of Helices (H), Strands (E), and Coils (C).
*   `scripts/analysis/calculate_mcc.py` – Performs model validation by computing the Matthews Correlation Coefficient against DisProt experimental data.
*   `scripts/analysis/filter_induced_disorder.py` – Identifies "Induced Fit" regions (MoRFs) by finding conflicts between disorder and structural propensity.
*   `scripts/analysis/filter_ss.py` – Screens for super-helical scaffolds using the custom SHS-score.
*   `scripts/analysis/summarize_test_stats.py` – Parses logs to extract execution time and memory usage metrics.
*   `scripts/analysis/pct_merge.py` – Merges individual statistics into the final summary tables used in the report.

## Environment & Installation

### ProtBert installation and activation
```shell
# 1. Create and activate virtual environment
python3 -m venv venv_ProtBert
source venv_ProtBert/bin/activate

# 2. Install required dependencies
pip install torch transformers sentencepiece

# 3. Download and save ProtBert model to local folder
python3 -c '
from transformers import AutoTokenizer, AutoModelForTokenClassification
model_name = "Rostlab/prot_bert_bfd_ss3"
save_path = "model_bert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)
```

```
# 1. Download IUPred3 archive
wget [https://iupred.elte.hu/static/iupred2a.tar.gz](https://iupred.elte.hu/static/iupred2a.tar.gz)

# 2. Extract and rename directory to match wrappers
tar -xzf iupred2a.tar.gz
mv iupred2a_src iupred2a 

# 3. Verify path
# Ensure the "iupred_path" in IUpred_wrapper.py points to this directory
```