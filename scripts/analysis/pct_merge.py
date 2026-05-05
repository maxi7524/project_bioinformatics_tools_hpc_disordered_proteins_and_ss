import os
import csv
import sys
import argparse

def format_species_name(name):
    """Maps internal file naming to formal report names."""
    mapping = {
        'E_coli': 'E. coli',
        'H_sapiens': 'H. sapiens',
        'SwissProt': 'SwissProt'
    }
    return mapping.get(name, name)

def merge_csv_files(input_dir, output_dir, iupred_filename, ss_filename):
    """Merges individual CSV results into two summary tables"""
    iupred_data = []
    ss_data = []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Paths for output files
    output_iupred = os.path.join(output_dir, iupred_filename)
    output_ss = os.path.join(output_dir, ss_filename)

    # Iterate through files in the input directory[cite: 6]
    files = sorted(os.listdir(input_dir))
    
    for filename in files:
        if not filename.endswith('.csv'):
            continue
            
        path = os.path.join(input_dir, filename)
        parts = filename.replace('.csv', '').split('_')
        
        # Determine species name based on naming convention
        if len(parts) > 2 and (parts[1] == 'sapiens' or parts[1] == 'coli'):
            species_raw = parts[0] + '_' + parts[1]
        else:
            species_raw = parts[0]

        species_name = format_species_name(species_raw)

        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader, None)
            if not row:
                continue

            if 'iupred' in filename:
                # Group IUPred data (short vs long)[cite: 5, 6]
                mode = 'short' if 'short' in filename else 'long'
                iupred_data.append({
                    'Species': species_name,
                    'Mode': mode,
                    'Total_AA': row['Total_AA'],
                    'Disorder_Pct': row['Disorder_Pct']
                })
            elif 'ss' in filename:
                # Group secondary structure data[cite: 5, 7]
                ss_data.append({
                    'Species': species_name,
                    'Total_AA': row['Total_AA'],
                    'Helix_Pct': row['Helix_Pct'],
                    'Strand_Pct': row['Strand_Pct'],
                    'Coil_Pct': row['Coil_Pct']
                })

    # Save Merged IUPred Table[cite: 5, 7]
    with open(output_iupred, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Species', 'Mode', 'Total_AA', 'Disorder_Pct'])
        writer.writeheader()
        writer.writerows(iupred_data)

    # Save Merged SS Table[cite: 5, 7]
    with open(output_ss, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Species', 'Total_AA', 'Helix_Pct', 'Strand_Pct', 'Coil_Pct'])
        writer.writeheader()
        writer.writerows(ss_data)

    print(f"Successfully merged data into:")
    print(f"  - {output_iupred}")
    print(f"  - {output_ss}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge protein structure prediction CSVs.")
    
    # Arguments for paths and filenames
    parser.add_argument("-i", "--input_dir", default="structure_pct", help="Directory containing partial CSVs")
    parser.add_argument("-o", "--output_dir", default="report/results", help="Directory to save final tables")
    parser.add_argument("--iupred_name", default="iupred_disorder_results.csv", help="Name of the merged IUPred file")
    parser.add_argument("--ss_name", default="ss_pcr_results.csv", help="Name of the merged SS file")

    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' not found.")
    else:
        merge_csv_files(args.input_dir, args.output_dir, args.iupred_name, args.ss_name)