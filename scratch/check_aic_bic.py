import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

def main():
    print("Loading dataset...")
    df = pd.read_excel("Data_Table_S5.xlsx", header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    
    # Filter to Regional Aquifer springs (N=45)
    reg = df[df["Aquifer Type"] == "Regional Aq"].copy()
    
    taxa = ["Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
    features_15 = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                   "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                   "Diversion", "Equine", "Cattle", "Recreate"]
    
    print("\n" + "="*50)
    print("Poisson GLM Fit Statistics (AIC and BIC)")
    print("="*50)
    
    for taxon in taxa:
        y = reg[taxon].astype(float)
        feats = features_15 if taxon == "Non Natives" else features_15 + ["Non Natives"]
        
        X_raw = reg[feats].astype(float)
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(scaler.fit_transform(X_raw), columns=feats, index=reg.index)
        X_const = sm.add_constant(X_scaled)
        
        # Fit Poisson GLM
        glm = sm.GLM(y, X_const, family=sm.families.Poisson()).fit()
        
        # In statsmodels GLM, bic is often computed as deviance + k * log(n)
        # statsmodels results has aic and bic_deviance properties
        k = len(glm.params)
        n = len(y)
        bic = glm.deviance + k * pd.np.log(n) if hasattr(pd, 'np') else glm.deviance + k * 3.806662 # log(45) approx 3.806662
        
        print(f"\nTaxon: {taxon}")
        print(f"  AIC: {glm.aic:.4f}")
        print(f"  BIC (Deviance-based): {glm.bic_deviance:.4f}")
        print(f"  BIC (Standard formulas): {bic:.4f}")
        print(f"  Deviance: {glm.deviance:.4f}")
        print(f"  Pearson chi2: {glm.pearson_chi2:.4f}")

if __name__ == "__main__":
    main()
