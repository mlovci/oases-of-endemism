import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, optimal_leaf_ordering
from scipy.spatial.distance import pdist

df = pd.read_excel('Data_Table_S5.xlsx', header=[0, 1])
df.columns = df.columns.get_level_values(0)
features = ["Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
X = df[features].astype(float)
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features)

dists_rows = pdist(X_scaled.values, metric='euclidean')
Z_rows = linkage(dists_rows, method='average')
Z_rows_ordered = optimal_leaf_ordering(Z_rows, dists_rows)

dists_cols = pdist(X_scaled.T.values, metric='correlation')
Z_cols = linkage(dists_cols, method='average')
Z_cols_ordered = optimal_leaf_ordering(Z_cols, dists_cols)

color_map = {
    "Regional Aq": "#17becf",
    "Local Hot": "red",
    "Local Cold": "#000080"
}
row_colors = df["Aquifer Type"].map(color_map)
row_colors.name = "Aquifer Type"

g = sns.clustermap(
    X_scaled,
    row_linkage=Z_rows_ordered,
    col_linkage=Z_cols_ordered,
    row_colors=row_colors,
    cmap="coolwarm",
    center=0,
    vmin=-2.5,
    vmax=2.5,
    yticklabels=False,
    figsize=(12, 10),
    cbar_kws={"label": "Standardized Value (Z-Score)", "orientation": "horizontal"},
    dendrogram_ratio=(0.12, 0.12)
)

g.ax_cbar.set_position([0.15, 0.05, 0.35, 0.02])

plt.gcf().canvas.draw()
print("Figure 6 Axes positions:")
print("  heatmap   :", g.ax_heatmap.get_position())
print("  row_dend  :", g.ax_row_dendrogram.get_position())
print("  col_dend  :", g.ax_col_dendrogram.get_position())
print("  row_colors:", g.ax_row_colors.get_position())
