import pandas as pd
import numpy as np

def simper_species(df, group_col, target_groups, variables):
    group_a = df[df[group_col] == target_groups[0]][variables].values
    group_b = df[df[group_col] == target_groups[1]][variables].values
    
    n_a = len(group_a)
    n_b = len(group_b)
    
    print(f"\nSIMPER Analysis between {target_groups[0]} (N={n_a}) and {target_groups[1]} (N={n_b}):")
    
    dissims = []
    for i in range(n_a):
        for j in range(n_b):
            pair_diff = np.abs(group_a[i] - group_b[j])
            pair_sum = group_a[i] + group_b[j]
            total_sum = np.sum(pair_sum)
            
            if total_sum == 0:
                spec_contr = np.zeros_like(pair_diff)
            else:
                spec_contr = pair_diff / total_sum
            dissims.append(spec_contr)
            
    dissims = np.array(dissims) # shape: (n_a * n_b, n_variables)
    mean_contr = np.mean(dissims, axis=0)
    std_contr = np.std(dissims, axis=0)
    
    total_mean_dissim = np.sum(mean_contr)
    
    results = []
    for idx, var in enumerate(variables):
        pct_contr = mean_contr[idx] / total_mean_dissim if total_mean_dissim > 0 else 0
        results.append({
            "Variable": var,
            "Mean Contribution": mean_contr[idx],
            "Contribution %": pct_contr * 100,
            "SD Contribution": std_contr[idx]
        })
        
    results_df = pd.DataFrame(results).sort_values(by="Mean Contribution", ascending=False)
    results_df["Cumulative Contribution %"] = results_df["Contribution %"].cumsum()
    
    print(f"Overall Average Dissimilarity: {total_mean_dissim:.4f}")
    for idx, r in results_df.iterrows():
        print(f"  - {r['Variable']:15}: Mean Contrib={r['Mean Contribution']:.4f} ({r['Contribution %']:.2f}%) | Cumulative={r['Cumulative Contribution %']:.2f}%")

def main():
    print("Loading dataset...")
    df = pd.read_excel("Data_Table_S5.xlsx", header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    
    biological_vars = ['Endemics', 'Crenophilies', 'Springsnails', 'Non Natives', 'Native Fish']
    
    simper_species(df, "Aquifer Type", ["Regional Aq", "Local Cold"], biological_vars)
    simper_species(df, "Aquifer Type", ["Regional Aq", "Local Hot"], biological_vars)
    simper_species(df, "Aquifer Type", ["Local Hot", "Local Cold"], biological_vars)

if __name__ == "__main__":
    main()
