import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, optimal_leaf_ordering
from scipy.spatial.distance import pdist

# Set styling for publication-quality plots
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "DejaVu Sans"],
    "figure.titlesize": 14,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "savefig.bbox": "tight"
})

def main():
    print("Loading dataset for site-level hierarchical clustering...")
    df = pd.read_excel('Data_Table_S5.xlsx', header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    
    # 5 biological variables to cluster
    features = ["Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
    
    # Extract data, apply square root transformation to the biological data prior to analysis as described in the paper
    X = df[features].astype(float)
    X_transformed = np.sqrt(X)
    
    # Standardize (z-score normalization) to put all metrics on the same visual scale
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_transformed), columns=features)
    
    # 1. Row Clustering (Spring Sites, N = 1121) using Euclidean distance and OLO
    print("Clustering rows (1121 springs)...")
    dists_rows = pdist(X_scaled.values, metric='euclidean')
    Z_rows = linkage(dists_rows, method='average')
    # OLO ensures leaves are ordered optimally to minimize distance between adjacent rows
    Z_rows_ordered = optimal_leaf_ordering(Z_rows, dists_rows)
    
    # 2. Column Clustering (Variables, N = 5) using correlation distance and OLO
    print("Clustering columns (5 variables)...")
    dists_cols = pdist(X_scaled.T.values, metric='correlation')
    Z_cols = linkage(dists_cols, method='average')
    Z_cols_ordered = optimal_leaf_ordering(Z_cols, dists_cols)
    
    # 3. Define Row Colors for Aquifer Type to show how clustering separates the groups
    # Regional Aq: Teal/Cyan, Local Hot: Red, Local Cold: Dark Blue
    color_map = {
        "Regional Aq": "#17becf",
        "Local Hot": "red",
        "Local Cold": "#000080"
    }
    row_colors = df["Aquifer Type"].map(color_map)
    row_colors.name = "Aquifer Type"
    
    # 4. Generate the Clustermap
    print("Plotting clustered heatmap...")
    g = sns.clustermap(
        X_scaled,
        row_linkage=Z_rows_ordered,
        col_linkage=Z_cols_ordered,
        row_colors=row_colors,
        cmap="coolwarm",
        center=0,
        vmin=-2.5,
        vmax=2.5,
        yticklabels=False,  # 1121 labels would overlap and be unreadable
        figsize=(12, 10),
        cbar_kws={"label": "Standardized Value (Z-Score)", "orientation": "vertical"},
        dendrogram_ratio=(0.12, 0.12)
    )
    
    # Adjust subplot margins to make room at the top (for title) and bottom (for labels)
    g.fig.subplots_adjust(top=0.90, bottom=0.15)
    
    # Position the vertical color bar on the right side below the legends to avoid label overlap
    g.ax_cbar.set_position([1.05, 0.35, 0.02, 0.15])
    g.ax_cbar.tick_params(labelsize=8)
    g.ax_cbar.yaxis.label.set_size(9)
    
    # 5. Color-code the Column Labels on the x-axis to highlight different categories
    # Teal: Native Biology, Purple: Non-Natives
    label_colors = {
        # Native Biology (Teal)
        "Endemics": "#008080",
        "Crenophilies": "#008080",
        "Springsnails": "#008080",
        "Native Fish": "#008080",
        
        # Non-Natives (Purple)
        "Non Natives": "#800080"
    }
    
    # Relabel columns to be more readable
    relabel_mapping = {
        "Endemics": "Endemic Richness",
        "Crenophilies": "Crenophile Richness",
        "Springsnails": "Springsnail Richness",
        "Native Fish": "Native Fish Richness",
        "Non Natives": "Non-Native Richness"
    }
    
    # Get ordered columns from clustermap
    x_labels = [relabel_mapping.get(feat, feat) for feat in X_scaled.columns[g.dendrogram_col.reordered_ind]]
    g.ax_heatmap.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10, fontweight='bold')
    
    for label in g.ax_heatmap.get_xticklabels():
        # Map back to original feature name to find color
        text = label.get_text()
        # Find original name by reversing relabel_mapping
        orig_name = None
        for k, v in relabel_mapping.items():
            if v == text:
                orig_name = k
                break
        
        if orig_name and orig_name in label_colors:
            label.set_color(label_colors[orig_name])
            
    # Remove x-axis tick lines for clean design
    g.ax_heatmap.tick_params(axis='both', which='both', length=0)
    
    # 6. Add Custom Legend for Row Colors (Aquifer Types) and Column Colors (Categories)
    # Legend for Row Colors
    from matplotlib.patches import Patch
    row_legend_elements = [
        Patch(facecolor="#17becf", edgecolor='none', label='Regional Aq (Stable Thermal)'),
        Patch(facecolor="red", edgecolor='none', label='Local Hot (Geothermal)'),
        Patch(facecolor="#000080", edgecolor='none', label='Local Cold (Ambient Runoff)')
    ]
    legend_row = g.ax_heatmap.legend(
        handles=row_legend_elements, 
        title="Spring Aquifer Type", 
        loc="upper left", 
        bbox_to_anchor=(1.05, 1.0), 
        fontsize=9, 
        title_fontsize=9,
        frameon=True,
        facecolor="whitesmoke"
    )
    # Add to heatmap axes
    g.ax_heatmap.add_artist(legend_row)
    
    # Legend for Column Colors
    col_legend_elements = [
        Patch(facecolor="#008080", edgecolor='none', label='Native Biology'),
        Patch(facecolor="#800080", edgecolor='none', label='Non-Native Biology')
    ]
    g.ax_heatmap.legend(
        handles=col_legend_elements, 
        title="Variable Category (Label Colors)", 
        loc="upper left", 
        bbox_to_anchor=(1.05, 0.75), 
        fontsize=9, 
        title_fontsize=9,
        frameon=True,
        facecolor="whitesmoke"
    )
    
    # Title
    g.fig.suptitle("Global Hierarchical Clustermap of Desert Springs\n(OLO clustering on 1121 springs and 5 standardized biological variables)", fontsize=13, fontweight='bold', y=0.97)
    
    # Ensure folder exists and save
    os.makedirs("figures", exist_ok=True)
    plt.savefig("figures/Figure_6_Global_Site_Clustering.png", dpi=300)
    plt.savefig("figures/Figure_6_Global_Site_Clustering.pdf", dpi=300)
    plt.close()
    print("Successfully generated global site clustermap: figures/Figure_6_Global_Site_Clustering.png and .pdf")

if __name__ == "__main__":
    main()
