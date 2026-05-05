import sys
import pandas as pd
import os

def get_disorder_fragments(disorder_map, min_len):
    """
    Identifies continuous disorder fragments ('D') that meet the minimum length requirement.
    """
    fragments = []
    current_start = None
    for i, char in enumerate(disorder_map):
        if char == 'D' and current_start is None:
            current_start = i
        elif char == '-' and current_start is not None:
            if (i - current_start) >= min_len:
                fragments.append((current_start, i - 1))
            current_start = None
    if current_start is not None and (len(disorder_map) - current_start) >= min_len:
        fragments.append((current_start, len(disorder_map) - 1))
    return fragments

def filter_induced():
    # Arguments: 1:IUPred file, 2:ProtBert file, 3:top_N, 4:min_dis_len, 5:max_coil%, 6:rem_dup
    dis_file = sys.argv[1]
    ss_file = sys.argv[2]
    num_top = int(sys.argv[3])
    min_dis_len = int(sys.argv[4])
    max_coil_pct = float(sys.argv[5])

    ss_data = {}
    with open(ss_file, 'r') as f:
        while True:
            h = f.readline().strip()
            s = f.readline().strip()
            ss = f.readline().strip()
            _ = f.readline().strip()
            if not h: break
            ss_data[h.split()[0]] = ss

    final_results = []
    df_list = []
    seen = set()
    remove_duplicates = sys.argv[6] == '1'

    with open(dis_file, 'r') as f:
        while True:
            h = f.readline().strip()
            s = f.readline().strip()
            dm = f.readline().strip()
            _ = f.readline().strip()
            if not h: break

            key = h.split()[0]
            if remove_duplicates and key in seen: continue

            if key in ss_data:
                ss = ss_data[key]
                frags = get_disorder_fragments(dm, min_dis_len)
                hits_info = []
                max_protein_score = -float('inf')

                for start, end in frags:
                    sub_ss = ss[start:end+1]
                    h_cnt, e_cnt, c_cnt = sub_ss.count('H'), sub_ss.count('E'), sub_ss.count('C')
                    coil_pct = (c_cnt / len(sub_ss)) * 100
                    
                    if coil_pct <= max_coil_pct:
                        score = (2 * h_cnt) + (2 * e_cnt) - (4 * c_cnt)
                        max_protein_score = max(max_protein_score, score)
                        hits_info.append(f"disorder[{start+1}-{end+1}]:H:{h_cnt},E:{e_cnt},-:{c_cnt},InducedDIS-score={score}")
                        
                        df_list.append({
                            'UID': key,
                            'Fragment': f"{start+1}-{end+1}",
                            'IndDis_Score': score,
                            'H_cnt': h_cnt,
                            'E_cnt': e_cnt,
                            'C_cnt': c_cnt
                        })

                if hits_info:
                    new_header = f"{h}|{', '.join(hits_info)}"
                    final_results.append((max_protein_score, new_header, s, dm, ss))
                    seen.add(key)

    final_results.sort(key=lambda x: x[0], reverse=True)
    
    # Save top UNIQUE results to CSV
    

    df = pd.DataFrame(df_list).sort_values(by='IndDis_Score', ascending=False).head(num_top)
    
    results_folder = "report/results/"
    filename = os.path.basename(dis_file)
    output_csv = os.path.join(results_folder, filename.replace('.fasta', '_Induced_results.csv'))
    df.to_csv(output_csv, index=False)

    for res in final_results[:num_top]:
        print(f"{res[1]}\n{res[2]}\n{res[3]}\n{res[4]}")

if __name__ == "__main__":
    filter_induced()