#!/bin/bash

# Usage: ./run_on_ram.sh <python_script> <input_fasta> <output_dir> <ram_base_path> [extra_python_args]
# Example: ./run_on_ram.sh iupred_runner.py data/set1/test.fasta results /dev/shm --stats

mkdir -p "$3"

PYTHON_SCRIPT=$(realpath "$1")
INPUT_FILE=$(realpath "$2")
OUTPUT_DIR=$(realpath "$3")
# IMPORTANT: Need to be absolute 
RAM_BASE="$4"
shift 4 

# Validation
if [ -z "$RAM_BASE" ]; then
    echo "Error: Missing RAM base path (e.g., /dev/shm or /tmp)"
    exit 1
fi

# 1. Create a descriptive temporary directory name
## Extract the name of the directory containing the input file
PARENT_DIR_NAME=$(basename "$(dirname "$INPUT_FILE")")
BASE_NAME=$(basename "$INPUT_FILE" .fasta)
## Structure: RAM_PATH/folderName_fileName_randomID # 
TEMP_DIR="${RAM_BASE}/${PARENT_DIR_NAME}_${BASE_NAME}_$RANDOM"

echo "Creating temporary workspace in RAM: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 2. Prepare files in RAM
## Copy input & script to RAM directory
cp "$INPUT_FILE" "$TEMP_DIR/input.fasta"
cp "$PYTHON_SCRIPT" "$TEMP_DIR/runner.py"

## Transition to RAM directory
cd "$TEMP_DIR"

# 3. Execute the script
## We pass local paths (input.fasta/output.fasta) and all remaining arguments
echo "Executing runner.py with extra args: $@"
python3 runner.py -i input.fasta -o output.fasta "$@"

# 4. Transfer results and cleanup
## create output dir 
mkdir -p "$OUTPUT_DIR"
## copying fasta outputs
if [ -f "output.fasta" ]; then
    cp output.fasta "$OUTPUT_DIR/${BASE_NAME}_pred.fasta"
    echo "Results saved to $OUTPUT_DIR/${BASE_NAME}_pred.fasta"
fi

## Copy stats if they exist (assuming default name stats.csv in python scripts)
STATS_FILENAME=""
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
    if [[ "${args[i]}" == "--stats_path" || "${args[i]}" == "--stats-path" ]]; then
        STATS_FILENAME="${args[i+1]}"
    fi
done

## Copying stats
if [ -n "$STATS_FILENAME" ] && [ -f "$STATS_FILENAME" ]; then
    ### If we gave different stats path 
    cp "$STATS_FILENAME" "$OUTPUT_DIR/$STATS_FILENAME"
    echo "Statistics saved to $OUTPUT_DIR/$STATS_FILENAME"
elif [ -f "stats.csv" ]; then
    ### If flag for name was not given but default file exists
    cp stats.csv "$OUTPUT_DIR/${BASE_NAME}_stats.csv"
    echo "Default statistics saved."
fi

# Cleanup temp dir on RAM 
rm -rf "$TEMP_DIR"
echo "Workspace cleaned."