import argparse
import time
import os
import resource
import csv
import sys

# params
## path to iupred 
iupred_path = "/home/ms488923/repositories/project_bioinformatics_tools_hpc_disordered_proteins_and_ss/iupred2a"


# Load part 
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    # Add iupred path to sys.path if not already present
    if iupred_path not in sys.path:
        sys.path.append(iupred_path)

    import iupred2a_lib
except ImportError:
    print("Error: iupred2a_lib.py not found in the specified directory.")
    sys.exit(1)

def run_iupred_logic(seq, mode):
    """
    Call iupred functions directly from the library.
    """
    # iupred2a_lib.iupred returns a tuple: (results_list, glob_text)
    scores, glob_text = iupred2a_lib.iupred(seq, mode)
    return scores

def parse_scores_to_fasta(scores):
    """
    Format raw scores into the required output format.
    """
    disorder_map = ""
    scores_scale = ""
    
    for score in scores:
        # threshold: >= 0.5 is 'D', otherwise '-'
        disorder_map += 'D' if score >= 0.5 else '-'
        # 0-9 scale for the pseudo-fasta output
        scores_scale += str(min(9, int(score * 10)))
        
    return disorder_map, scores_scale

def main():
    parser = argparse.ArgumentParser(description="IUPred CPU Wrapper")
    parser.add_argument("-i", "--input", required=True, help="Input flat FASTA file")
    parser.add_argument("-o", "--output", required=True, help="Output pseudo-FASTA file")
    parser.add_argument("--exec_mode", choices=['long', 'short', 'glob'], default='short', 
                        help="Prediction mode (default: short)")
    parser.add_argument("--mode", choices=['normal', 'test'], default='normal', 
                        help="Execution mode for stats")
    parser.add_argument("--stats_path", help="Path to save CSV stats (required in test mode)")
    
    args = parser.parse_args()
    
    stats_data = []
    
    # Process sequences
    with open(args.input, 'r') as f_in, open(args.output, 'w') as f_out:
        while True:
            header = f_in.readline().strip()
            seq = f_in.readline().strip()
            if not header or not seq: 
                break
            
            start_time = time.perf_counter()
            
            # Run prediction
            scores = run_iupred_logic(seq, args.exec_mode)
            disorder, scale = parse_scores_to_fasta(scores)
            
            end_time = time.perf_counter()
            
            # Write pseudo-FASTA output
            f_out.write(f"{header}\n{seq}\n{disorder}\n{scale}\n")
            
            if args.mode == 'test':
                # Measure current process memory usage (MB)
                mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                stats_data.append({
                    'length': len(seq),
                    'time': end_time - start_time,
                    'memory': mem_usage
                })

    # Save performance stats to CSV
    if args.mode == 'test' and args.stats_path:
        if stats_data:
            keys = stats_data[0].keys()
            with open(args.stats_path, 'w', newline='') as f_stats:
                dict_writer = csv.DictWriter(f_stats, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(stats_data)

if __name__ == "__main__":
    main()