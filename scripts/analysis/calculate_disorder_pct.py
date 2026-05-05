import sys
import csv
import os

def calculate_disorder(input_file, csv_output):
    total_aa = 0
    total_disorder = 0

    # Parse 4-line pseudo-FASTA format
    with open(input_file, 'r') as f:
        while True:
            header = f.readline().strip()
            seq = f.readline().strip()
            disorder_map = f.readline().strip()
            scores = f.readline().strip()
            
            if not header:
                break
            
            total_aa += len(seq)
            total_disorder += disorder_map.count('D')

    if total_aa == 0:
        print("Error: Input file is empty.")
        return

    disorder_pct = (total_disorder / total_aa) * 100
    
    # Print results to console
    print(f"File: {input_file}")
    print(f"Total AA: {total_aa}")
    print(f"Disorder content: {disorder_pct:.2f}%")

    # Save to CSV 
    file_exists = os.path.isfile(csv_output)
    with open(csv_output, 'a', newline='') as csvfile:
        fieldnames = ['File', 'Total_AA', 'Disorder_Pct']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'File': input_file,
            'Total_AA': total_aa,
            'Disorder_Pct': round(disorder_pct, 2)
        })

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 calc_disorder_pct.py <input_fasta> <output_csv>")
    else:
        calculate_disorder(sys.argv[1], sys.argv[2])