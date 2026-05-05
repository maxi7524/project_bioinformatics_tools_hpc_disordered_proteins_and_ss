#!/bin/bash

# params
## Directory containing split data
BASE_SPLIT="data/splitted"
## Directory for output results
BASE_RESULTS="data/results/IUpred/long"
## List of organisms to process
ORGANISMS=("E_coli" "H_sapiens" "SwissProt")
## Active jobs limit
MAX_JOBS=2


# Iterarate through all organizm folders
for ORG in "${ORGANISMS[@]}"; do
    echo "--- Processing organism: $ORG ---"
    ## Create output dirs
    mkdir -p "$BASE_RESULTS/$ORG"
    mkdir -p "logs/iupred/long"

    # Iterate through all fasta files for given organizm
    for FASTA in "$BASE_SPLIT/$ORG"/*.fasta; do
        # Skip, if dir is empty
        [ -e "$FASTA" ] || continue
        
        FILENAME=$(basename "$FASTA")
        OUT_PATH="$BASE_RESULTS/$ORG/${FILENAME%.fasta}_pred.fasta"

        # PROGRESS CHECK: Skip if the result file already exists
        if [[ -f "$OUT_PATH" ]]; then
            echo "Skipping (already exists): $FILENAME"
            continue
        fi

        # --- QUEUE CONTROL MECHANISM ---
        # Count user jobs (both Running 'R' and Pending 'PD')
        # -h removes the header, -t filters by status
        while [ $(squeue -u $USER -h -t PD,R | wc -l) -ge $MAX_JOBS ]; do
            echo "Limit of $MAX_JOBS jobs reached. Waiting 10 seconds..."
            sleep 10
        done

        echo "Submitting job for: $FILENAME"
        # Submit the job to Slurm passing input and output paths
        sbatch scripts/sbatch/job_IUPred_long.sbatch "$FASTA" "$OUT_PATH"
        
        # Wait to avoid skipping job by slurm 
        sleep 1
    done
done