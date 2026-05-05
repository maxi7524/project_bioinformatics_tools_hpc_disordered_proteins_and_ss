import sys
import csv
import os

def calculate_ss(input_file, csv_output):
    total_aa = 0
    counts = {'H': 0, 'E': 0, '-': 0}

    # Parse 4-line pseudo-FASTA format
    with open(input_file, 'r') as f:
        while True:
            header = f.readline().strip()
            seq = f.readline().strip()
            ss_map = f.readline().strip()
            conf = f.readline().strip()
            
            if not header:
                break
            
            total_aa += len(seq)
            counts['H'] += ss_map.count('H')
            counts['E'] += ss_map.count('E')
            counts['-'] += len(seq) - ss_map.count('H') - ss_map.count('E')

    if total_aa == 0:
        print("Error: Input file is empty.")
        return

    results = {'File': input_file, 'Total_AA': total_aa}
    print(f"File: {input_file}")
    
    for char, count in counts.items():
        name = "Helix" if char == 'H' else "Strand" if char == 'E' else "Coil"
        pct = (count / total_aa) * 100
        results[f"{name}_Pct"] = round(pct, 2)
        print(f"{name} ({char}): {pct:.2f}%")

    # Save to CSV 
    file_exists = os.path.isfile(csv_output)
    with open(csv_output, 'a', newline='') as csvfile:
        fieldnames = ['File', 'Total_AA', 'Helix_Pct', 'Strand_Pct', 'Coil_Pct']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(results)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 calc_ss_pct.py <input_fasta> <output_csv>")
    else:
        calculate_ss(sys.argv[1], sys.argv[2])