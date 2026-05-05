import pandas as pd
import argparse
import os

def summarize(input_csv, save_path=None):
    if not os.path.exists(input_csv):
        print(f"Error: File {input_csv} does not exist.")
        return

    # Load data
    df = pd.read_csv(input_csv)
    
    # Basic length and time statistics
    avg_len = df['length'].mean()
    avg_time = df['time'].mean()
    total_seq = len(df)
    
    # Memory statistics (MB)
    avg_mem = df['memory'].mean()
    max_mem = df['memory'].max()
    
    # Scaling: time per single amino acid (ms)
    df['ms_per_aa'] = (df['time'] / df['length']) * 1000
    avg_ms_per_aa = df['ms_per_aa'].mean()
    
    # Correlation of length to time (does time depends on length)
    correlation = df['length'].corr(df['time'])

    print(f"\n=== PERFORMANCE REPORT: {os.path.basename(input_csv)} ===")
    print(f"Number of analyzed sequences:       {total_seq}")
    print(f"Average sequence length:            {avg_len:.2f} aa")
    print(f"Average time per sequence:          {avg_time:.4f} s")
    print(f"Average time per amino acid:        {avg_ms_per_aa:.2f} ms")
    print(f"Average memory usage:               {avg_mem:.2f} MB")
    print(f"Peak memory usage:                  {max_mem:.2f} MB")
    print(f"Correlation coefficient (len/time): {correlation:.4f}")
    
    if correlation > 0.9:
        print("Characteristics: Linear scaling (predictable).")
    else:
        print("Characteristics: Non-linear scaling or high overhead.")

    # Projection for the entire proteome (i used human for refrence)
    est_human = (avg_time * 20_000) / 3600
    print(f"\nEstimated time for human proteome (20k proteins) on 1 CPU: {est_human:.2f} h")
    print("==========================================\n")

    # if save parameter is given:
    if save_path is not None:
        report_data = {
            'Metric': [
                'Source File', 'Total Sequences', 'Avg Length [aa]', 
                'Avg Time/Seq [s]', 'Avg Time/AA [ms]', 'Avg Memory [MB]', 
                'Max Memory [MB]', 'Correlation', 'Human Proteome Est (20k prot) [h]'
            ],
            'Value': [
                os.path.basename(input_csv), total_seq, round(avg_len, 2), 
                round(avg_time, 4), round(avg_ms_per_aa, 2), round(avg_mem, 2),
                round(max_mem, 2), round(correlation, 4), round(est_human, 2)
            ]
        }
        report_df = pd.DataFrame(report_data)
        
        # Return result to csv 
        report_df.to_csv(save_path, index=False)
        print(f"Report saved to: {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Path to the _stats.csv file")
    parser.add_argument("-s", "--save", default=None, help="Path to save the summary report (e.g. report.csv)")
    args = parser.parse_args()
    summarize(args.input, args.save)