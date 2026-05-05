#!/bin/bash -l
#SBATCH --job-name=iupred_part
#SBATCH --partition=common
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1      
#SBATCH --time=00:15:00    # it maximally takes 2-3 min 
#SBATCH --output="logs/iupred/%j.out"
#SBATCH --error="logs/iupred/%j.err"

# params
INPUT_FILE=$1
OUTPUT_FILE=$2
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")

# activate environment
source $HOME/venv_ProtBert/bin/activate

# Execute using RAM-disk helper
# Args order: 1. Wrapper script, 2. Input file, 3. Output directory, 4. RAM path, 5. additional flags
./scripts/helpers/run_on_ram.sh \
    scripts/wrappers/ProtBert_wrapper.py \
    "$INPUT_FILE" \
    "$OUTPUT_DIR" \
    /dev/shm \
    --mode normal \
    --device 0