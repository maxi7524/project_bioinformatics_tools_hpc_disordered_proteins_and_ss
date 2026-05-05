import sys
import pandas as pd
from sklearn.metrics import matthews_corrcoef
import os

def parse_disprot_fragments(csv_file):
    """
    Parses the DisProt CSV file to extract experimental disorder fragments.
    """
    df = pd.read_csv(csv_file)
    truth = {}
    for _, row in df.iterrows():
        acc = row['acc']
        frags = row['fragments'].replace('[', '').split(']')
        truth[acc] = []
        for f in frags:
            if f:
                start, end = map(int, f.split('-'))
                truth[acc].append((start, end))
    return truth

def calculate_mcc():
    fasta_file = sys.argv[1]
    csv_file = sys.argv[2]
    
    disprot_truth = parse_disprot_fragments(csv_file)
    y_true, y_pred = [], []

    with open(fasta_file, 'r') as f:
        while True:
            h = f.readline().strip()
            s = f.readline().strip()
            pred_map = f.readline().strip()
            conf = f.readline().strip()
            if not h: break

            acc = h.split('|')[1]
            if acc in disprot_truth:
                true_vec = [0] * len(s)
                for start, end in disprot_truth[acc]:
                    for i in range(start-1, end):
                        if i < len(true_vec): true_vec[i] = 1
                
                pred_vec = [1 if c == 'D' else 0 for c in pred_map]
                y_true.extend(true_vec)
                y_pred.extend(pred_vec)

    score = matthews_corrcoef(y_true, y_pred)
    
    # Save MCC result to DataFrame
    mcc_df = pd.DataFrame({
        'File': [os.path.basename(fasta_file)],
        'MCC': [round(score, 4)]
    })
    

    results_folder = "report/results/"
    filename = os.path.basename(fasta_file)
    output_csv = os.path.join(results_folder, filename.replace('.fasta', '_mcc.csv'))
    mcc_df.to_csv(output_csv, index=False)
    
    print(f"MCC Score: {score:.4f} (Saved to {output_csv})")

if __name__ == "__main__":
    calculate_mcc()