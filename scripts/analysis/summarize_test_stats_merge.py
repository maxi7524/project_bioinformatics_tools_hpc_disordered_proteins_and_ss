import pandas as pd
import glob
import os
import argparse

def merge_reports(input_dir, output_path):
    """
    Collects individual CSV reports from input_dir and merges them 
    into a single summary table.
    """
    # Find all CSV files in the specified directory
    file_pattern = os.path.join(input_dir, "*.csv")
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"Error: No CSV files found in directory '{input_dir}'")
        return

    all_rows = []

    for file_path in files:
        try:
            # Read the report (format: Metric, Value)
            df = pd.read_csv(file_path)
            
            # Remove `Source File` - debbuging redundant information
            df = df[df['Metric'] != 'Source File']

            # Pivot the table: set Metric as index and transpose 
            summary_row = df.set_index('Metric').T
            
            
            # Use the filename (without extension) as the identifier 
            # to distinguish experiments (e.g., ProtBert_E_coli_gpu)
            experiment_name = os.path.splitext(os.path.basename(file_path))[0]
            summary_row['Experiment_ID'] = experiment_name
            
            # Ensure 'Source File' is present or updated from the filename
            summary_row.reset_index(drop=True, inplace=True)
            all_rows.append(summary_row)
            
        except Exception as e:
            print(f"Skipping file {file_path} due to error: {e}")

    # Combine all individual rows into one master DataFrame
    final_df = pd.concat(all_rows, ignore_index=True)

    # Reorder columns to put Experiment_ID first for better readability
    cols = ['Experiment_ID'] + [c for c in final_df.columns if c != 'Experiment_ID']
    final_df = final_df[cols]

    # Sort by experiment name to group tools and organisms together
    final_df = final_df.sort_values(by='Experiment_ID')

    # Save the final merged report to the specified path
    final_df.to_csv(output_path, index=False)
    print(f"Successfully merged {len(all_rows)} reports.")
    print(f"Final summary saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge individual performance reports into one table.")
    
    # Path to the folder containing the result CSVs
    parser.add_argument("-i", "--input_dir", required=True, 
                        help="Directory containing the individual .csv report files")
    
    # Full path including filename for the output
    parser.add_argument("-o", "--output_file", required=True, 
                        help="Full path and filename for the merged output (e.g., results/summary.csv)")

    args = parser.parse_args()

    merge_reports(args.input_dir, args.output_file)