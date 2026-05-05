import pandas as pd
import os

# -----------------
# Helpers
# -----------------

def format_organism(name):
    mapping = {
        'E_coli': '*E. coli*',
        'H_sapiens': '*H. sapiens*',
        'SwissProt': 'SwissProt'
    }
    return mapping.get(name, name)


def generate_consolidated_table(iupred_path, ss_path):
    # Load CSVs
    df_iupred = pd.read_csv(iupred_path)
    df_ss = pd.read_csv(ss_path)
    
    # We filter only 'long' version for the main summary table
    df_iupred_long = df_iupred[df_iupred['Mode'] == 'long'].copy()
    
    # Merge on Species/Organism
    merged = pd.merge(df_iupred_long, df_ss, on="Species")
    
    # Rename and select columns to match Homework requirements
    final_table = merged[['Species', 'Disorder_Pct', 'Helix_Pct', 'Strand_Pct', 'Coil_Pct']]
    # Note: 'Total Time' columns would need to be added from your log files or hardcoded
    return final_table.to_markdown(index=False)

def time_to_minutes(time_str):
    """Converts format H:MM:SS into MM:SS on minutes (float)."""
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 3: # H:MM:SS
        return round(parts[0] * 60 + parts[1] + parts[2] / 60, 2)
    elif len(parts) == 2: # MM:SS
        return round(parts[0] + parts[1] / 60, 2)
    return 0.0

def add_summary_row(df, label_col='Organism', label_text='**Total**'):
    """
    Adds a summary row at the bottom of the DataFrame with sums for all numeric columns.
    """
    # Select only numeric columns for summation
    numeric_df = df.select_dtypes(include=['number'])
    totals = numeric_df.sum()
    
    # Create the summary row as a DataFrame
    total_row = pd.DataFrame([totals])
    
    # Set the label in the specified identification column
    total_row[label_col] = label_text
    
    # Concatenate original df with the summary row
    return pd.concat([df, total_row], ignore_index=True)

# -----------------
# Main part
# -----------------

def generate_report():
    res_path = "report/results/"
    
    # --- SECTION 1: DATASETS ---
    section_1 = "## Datasets\n\n"
    section_1 += "### Model Organisms\n\n"
    section_1 += "In this study, we utilized *E. coli* and *H. sapiens* as model organisms, representing prokaryotic and eukaryotic proteomes respectively. ""
    section_1 += "*SwissProt* was used as a comprehensive database, providing a reference due to its high-quality, manually curated entries. "
    section_1 += "To ensure computational stability and avoid Out-Of-Memory (OOM) errors during ProtBert processing, all sequences exceeding 2500 amino acids were removed. \n\n"
    
    section_1 += "#### Dataset Summary\n\n"
    data_summary = {
        'Organism': ['*E. coli*', '*H. sapiens*', '*SwissProt*'],
        'Total Sequences': [4403, 20659, 574627],
        'Processed (<2500aa)': [4362, 20586, 486337]
    }

    section_1 += pd.DataFrame(data_summary).to_markdown(index=False) + "\n\n"

    section_1 += "#### Percentage of disorder \n\n"


    section_1 += generate_consolidated_table(
        os.path.join(res_path, "iupred_disorder_results.csv"),
        os.path.join(res_path, "ss_pcr_results.csv")
    ) +'\n\n'

    section_1 += "#TODO - conclusion\n\n"

    # --- SECTION 2: COMPUTATIONAL PERFORMANCE ---
    section_2 = "## Computational Performance\n\n"
    section_2 += "### Resource Scaling and Intuition\n\n"
    section_2 += "The primary objective was to investigate how processing time and memory usage scales with sequence length and organism type. "
    section_2 += "By analyzing these metrics, we aim to build intuition for resource estimation. \n\n"

    section_2 += "#### Time estimation results\n\n"
    if os.path.exists(res_path + "time_estimation_merged.csv"):
        # TODO - check if experiment ID had changed
        time_df = pd.read_csv(res_path + "time_estimation_merged.csv")
        time_df['Experiment_ID'] = time_df['Experiment_ID'].str.split('_').str[2:].str.join('-')
        time_df.rename(columns={'Experiment_ID': 'Experiment ID'})

        section_2 += time_df.to_markdown(index=False) + "\n\n"

    section_2 += "#### Total Execution Time\n\n"
    full_time_data = {
        'Organism': ['*E. coli*', '*H. sapiens*', '*SwissProt*'],
        'IUPred Short [min]': ['0:00:22', '0:02:24', '1:51:30'],
        'IUPred Long [min]': ['0:00:45', '0:06:12', '1:49:18'],
        'ProtBert [min]': ['0:01:24', '0:09:12', '2:30:52']
    }

    # Conversion to minute format
    df_time = pd.DataFrame(full_time_data)
    time_cols = ['IUPred Short [min]', 'IUPred Long [min]', 'ProtBert [min]']
    for col in time_cols:
        df_time[col] = df_time[col].apply(time_to_minutes)

    # Find total per organism time 
    df_time['Total [min]'] = df_time[time_cols].sum(axis=1).round(2)


    ##### TEST
    df_time = add_summary_row(df_time)

    # 4. Generujemy tabelę
    section_2 += df_time.to_markdown(index=False) + "\n\n"


    # section_2 += pd.DataFrame(df_time).to_markdown(index=False) + "\n\n"
    section_2 += "#### Performance Analysis\n\n#TODO: Analysis of scaling and intuition results.\n\n"

    # --- SECTION 3: DISPROT ANALYSIS ---
    section_3 = "## Model Validation against DisProt\n\n"
    section_3 += "### Comparative Study of IUPred Versions\n\n"
    section_3 += "We aimed to determine whether the 'short' or 'long' version of IUPred provides a more accurate representation of intrinsically disordered regions in human proteins. "
    section_3 += "To evaluate performance, we utilized the Matthews Correlation Coefficient (MCC) against experimentally validated fragments from DisProt. "
    section_3 += "MCC was chosen because it provides a balanced measure for binary classification.\n\n"

    mcc_results = []
    for f in ["iupred_short_mcc.csv", "iupred_long_mcc.csv"]:
        if os.path.exists(res_path + f):
            mcc_results.append(pd.read_csv(res_path + f))
    
    section_3 += "#### MCC Validation Results\n\n"
    if mcc_results:
        section_3 += pd.concat(mcc_results).to_markdown(index=False) + "\n\n"
    section_3 += "#### Comparison Analysis\n\n#TODO: Determine which IUPred version performed better.\n\n"

    # --- SECTION 4: INDUCED FIT DISORDER ---
    section_4 = "## Identification of Functional Transitions\n\n"
    section_4 += "### Search for Induced Fit Regions\n\n"
    section_4 += "We aimed to identify disordered regions that undergo structural transitions upon binding, known as induced fit, by contrasting IUPred’s energy-based disorder predictions with ProtBert’s secondary structure propensities."
    section_4 += "We specifically isolate 'conflicting' fragments—predicted as disordered by IUPred but assigned high structural confidence (helices or strands) by ProtBert—to pinpoint potential Molecular Recognition Features (MoRFs). "
    section_4 += "This approach is justified by the hypothesis that these regions possess a latent structural preference that only manifests upon contact with a binding partner, distinguishing functional interaction sites from permanently disordered segments.\n\n"
    section_4 += r"$$IndDis-score = (2 \cdot H) + (2 \cdot E) - (4 \cdot -)$$" + "\n\n"

    section_4 += "#### Top Candidates (Induced Fit)\n\n"
    if os.path.exists(res_path + "iupred_long_Induced_results.csv"):
        induced_df = pd.read_csv(res_path + "iupred_long_Induced_results.csv").head(5)
        # TODO - check
        # take only sequence id  
        induced_df['UID'] = induced_df['UID'].str.split('|').str[1] 

        section_4 += induced_df.to_markdown(index=False) + "\n\n"
    section_4 += "#### Analysis\n\n#TODO: Evaluate the biological significance of these fragments.\n\n"

    # --- SECTION 5: DISCOVERY OF HELICAL SCAFFOLDS ---
    section_5 = "## Discovery of Helical Scaffolds\n\n"
    section_5 += "### Identification of Super-Helical Proteins\n\n"
    section_5 += "We performed screening of the SwissProt database to identify proteins with exceptional alpha-helical content. "
    section_5 += "By applying the SHS-score, we strictly filter for sequences that maximize helical propensity while penalizing coils and strands. \n\n"
    section_5 += r"$$SHS-score = \frac{[2 \cdot H + (-1) \cdot - + (-2) \cdot E]}{len(seq)}$$" + "\n\n"

    section_5 += "#### Top Candidates (SwissProt)\n\n"
    if os.path.exists(res_path + "ProtBert_SHS_results.csv"):
        shs_df = pd.read_csv(res_path + "ProtBert_SHS_results.csv").head(5)
        section_5 += shs_df.to_markdown(index=False) + "\n\n"
    section_5 += "#### Conclusion\n\n#TODO: Summarize the diversity of identified helical proteins.\n\n"
    section_5 += 'highly ordered building blocks—like coiled-coils or solenoids—that can be used as reliable templates for modular protein engineering and synthetic biology.'

    # --- FINAL MERGING ---
    final_report = section_1 + section_2 + section_3 + section_4 + section_5
    
    with open("report.md", "w") as f:
        f.write(final_report)
    print("Report generated: report.md")

if __name__ == "__main__":
    generate_report()