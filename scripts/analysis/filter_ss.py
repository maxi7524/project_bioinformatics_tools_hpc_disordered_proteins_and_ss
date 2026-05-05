import sys
import pandas as pd
import os

def calculate_shs(ss_seq, w_h, w_c, w_e):
    """
    Calculates the SHS-score based on the provided weights:
    SHS-score = [(H * w_h) + (C * w_c) + (E * w_e)] / len(seq)
    """
    h = ss_seq.count('H')
    e = ss_seq.count('E')
    c = ss_seq.count('-')
    return (h * w_h + c * w_c + e * w_e) / len(ss_seq)

def filter_ss():
    # Arguments: 
    # 1:input_file, 2:num_top, 3:min_len, 4:min_H%, 5:max_E%, 
    # 6:weight_H, 7:weight_C, 8:weight_E, 9:remove_duplicates[1/0]
    
    input_file = sys.argv[1]
    num_top = int(sys.argv[2])
    min_len = int(sys.argv[3])
    min_h_pct = float(sys.argv[4])
    max_e_pct = float(sys.argv[5])
    w_h = float(sys.argv[6])
    w_c = float(sys.argv[7])
    w_e = float(sys.argv[8])

    results = []
    seen = set()
    df_list = [] # List to collect data for DataFrame

    with open(input_file, 'r') as f:
        while True:
            h = f.readline().strip()   # Header
            s = f.readline().strip()   # Sequence
            ss = f.readline().strip()  # Secondary Structure
            conf = f.readline().strip() # Confidence/Score line
            if not h: break

            uid = h.split('|')[1]
            if sys.argv[9] == '1' and uid in seen: 
                continue
            
            if len(s) < min_len: 
                continue
            
            h_pct = (ss.count('H') / len(s)) * 100
            e_pct = (ss.count('E') / len(s)) * 100
            
            if h_pct >= min_h_pct and e_pct <= max_e_pct:
                score = calculate_shs(ss, w_h, w_c, w_e)
                new_header = f"{h}|SHS-score={score:.2f}"
                results.append((score, new_header, s, ss, conf))
                
                # Add data to the dictionary for DataFrame
                df_list.append({
                    'UID': uid,
                    'SHS_Score': round(score, 4),
                    'H_pct': round(h_pct, 2),
                    'E_pct': round(e_pct, 2),
                    'Length': len(s)
                })
                seen.add(uid)

    results.sort(key=lambda x: x[0], reverse=True)

    # Save to DataFrame for the final report
    df = pd.DataFrame(df_list).sort_values(by='SHS_Score', ascending=False).head(num_top)
    results_folder = "report/results/"
    filename = os.path.basename(input_file)
    output_csv = os.path.join(results_folder, filename.replace('.fasta', '_SHS_results.csv'))
    df.to_csv(output_csv, index=False)
    print(f"Results saved to DataFrame: {output_csv}")

    # Output top results in FASTA format
    for res in results[:num_top]:
        print(f"{res[1]}\n{res[2]}\n{res[3]}\n{res[4]}")

if __name__ == "__main__":
    filter_ss()