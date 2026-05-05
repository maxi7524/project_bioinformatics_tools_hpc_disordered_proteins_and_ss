import argparse
import torch
import time
import csv
import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


# params
## Path to loaded model
model_id = "/home/ms488923/model_bert"

def main():
    parser = argparse.ArgumentParser(description="ProtTrans GPU Wrapper")
    parser.add_argument("-i", "--input", required=True, help="Input flat FASTA file")
    parser.add_argument("-o", "--output", required=True, help="Output pseudo-FASTA file")
    parser.add_argument("--mode", choices=['normal', 'test'], default='normal', help="Execution mode")
    parser.add_argument("--stats_path", help="Path to save stats")
    parser.add_argument("--device", type=int, default=0, help="GPU device ID (default 0, -1 for CPU)")
    
    args = parser.parse_args()
    
    # Load model
    device = torch.device(f'cuda:{args.device}' if (torch.cuda.is_available() and args.device >= 0) else 'cpu')
    
    print(f"--- Model intialization : {model_id} ---")
    print(f"--- Model intialization : {device} ---")

    start_loading = time.perf_counter()
    pipe = pipeline("token-classification", model=model_id, 
                    tokenizer=AutoTokenizer.from_pretrained(model_id, skip_special_tokens=True), 
                    device=args.device)

    print(f"--- Model initialized: {time.perf_counter() - start_loading:.2f}s ---")

    stats_data = []

    with open(args.input, 'r') as f_in, open(args.output, 'w') as f_out:
        print("---Running sequences ...---")
        while True:
            header = f_in.readline().strip()
            seq = f_in.readline().strip()
            if not header or not seq: break
            
            # Format sequence for ProtBert (add spaces between aminoacids)
            formatted_seq = " ".join(list(seq))
            
            start_time = time.perf_counter()
            
            # Inference
            results = pipe(formatted_seq)
            
            end_time = time.perf_counter()
            
            # Parse secondary structure and scores
            ## Mapping: H=Helix, E=Strand, C=Coil (Standard SS3)
            ss_map = ""
            conf_scores = ""
            
            ## Align tokens (output) to sequence
            for res in results:
                ss_map += res['entity'][0] # Take first letter (H, E, L/C)
                conf_scores += str(min(9, int(res['score'] * 10)))
            
            f_out.write(f"{header}\n{seq}\n{ss_map}\n{conf_scores}\n")
            
            if args.mode == 'test':
                # Measure memory usage
                if torch.cuda.is_available():
                    gpu_mem = torch.cuda.max_memory_allocated(device=args.device) / 1024**2 # MB
                else:
                    gpu_mem = 0
                stats_data.append({
                    'length': len(seq),
                    'time': end_time - start_time,
                    'memory': gpu_mem,
                    'device': device.type
                })

    if args.mode == 'test' and args.stats_path:
        with open(args.stats_path, 'w', newline='') as f_stats:
            writer = csv.DictWriter(f_stats, fieldnames=stats_data[0].keys())
            writer.writeheader()
            writer.writerows(stats_data)

    print("--- Done---")

if __name__ == "__main__":
    main()