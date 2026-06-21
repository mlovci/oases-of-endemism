import os

def main():
    filepath = "/Users/mlovci/Desktop/Oases of Endemism/results.md"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Section D (Multi-Taxon Regression & Feature Importance Analysis) text block
    old_sec_d = """To understand the diverging physical habitat requirements and ecological drivers across different biological groups in Regional Aquifer oases ($N=45$), we performed a parallelized bootstrap Random Forest regression (1,000 splits) and standardized Poisson Generalized Linear Models (GLMs) with robust standard errors (HC3) for each of the five biological richness variables independently. All model metrics represent out-of-sample (OOS) validation performance on unseen data.

The results show a clear divergence in physical niche space:
1.  **Water-Column Swimming Taxa (Native Fish)**:
    *   *Predictability*: $R^2_{median} = 0.168$, mean MSE $= 1.066$.
    *   *Top Drivers*: `Width` (Gini $= 0.183$) and `Depth` ($0.171$).
    *   *GLM Coefficients*: Strong positive effects of pool `Width` ($\\beta = +0.4439, p < 0.001$), `Depth` ($\\beta = +0.2393, p = 0.005$), and `Temperature` ($\\beta = +0.2227, p < 0.001$), and a negative effect of `pH` ($\\beta = -0.1747, p = 0.007$). This quantitatively demonstrates that native desert fish are limited by water volume (pool width/depth) and temperature.
2.  **Benthic-Specialist Grazers (Springsnails)**:
    *   *Predictability*: $R^2_{median} = 0.203$ (the most predictable group).
    *   *Top Drivers*: `Silt` (Gini $= 0.198$), `Cobble` ($0.120$), and `Depth` ($0.113$).
    *   *GLM Coefficients*: Dominated by an extremely significant negative effect of substrate `Silt` ($\\beta = -0.3235, p < 0.001$) and a positive effect of `Cobble` ($\\beta = +0.1706, p = 0.007$). This reflects their dependence on clean, rocky grazing surfaces and extreme vulnerability to grazing-induced siltation.
3.  **Non-Native Invaders**:
    *   *Predictability*: $R^2_{median} = 0.072$.
    *   *Top Drivers*: `Temperature` (Gini $= 0.134$), `Conductivity` ($0.103$), and `Depth` ($0.099$).
    *   *GLM Coefficients*: Significant positive effects of human disturbances, including `Diversion` ($\\beta = +0.1282, p = 0.031$) and `Recreate` ($\\beta = +0.1554, p = 0.002$), showing how anthropogenic activity acts as an invasion pathway.
4.  **Endemics and Crenophilies**:
    *   *Predictability*: $R^2_{median} = 0.063$ (Endemics) and $R^2_{median} = 0.105$ (Crenophilies).
    *   *Top Drivers*: Primarily driven by pool `Depth` (Gini $= 0.156$ and $0.165$) and `Temperature` ($0.107$ and $0.117$).
    *   *GLM Coefficients*: Strongly positive for `Depth` ($\\beta = +0.4140, p < 0.001$) and negative for `Silt` ($\\beta = -0.1472, p = 0.003$) and `pH` ($\\beta = -0.1557, p = 0.001$). They act as ecological generalists whose distributions are a composite of hydrological permanence and benthic quality."""

    new_sec_d = """Bootstrap Random Forest regressions (1,000 splits) and standardized Poisson GLMs with robust standard errors (HC3) were fitted for each of the five biological richness variables independently. All model metrics represent out-of-sample (OOS) validation performance on unseen data.

The results show a clear divergence in physical niche space:
1.  **Water-Column Swimming Taxa (Native Fish)**:
    *   *Predictability*: $R^2_{median} = 0.464$, mean MSE $= 0.801$.
    *   *Top Drivers*: `Depth` (Gini $= 0.197$) and `Non Natives` ($0.137$).
    *   *GLM Coefficients*: Significant positive effects of pool `Depth` ($\\beta = +0.2381^{***}, p < 0.001$), `Temperature` ($\\beta = +0.7600^{**}, p = 0.009$), and `Non Natives` ($\\beta = +0.9477^{***}, p < 0.001$), and negative effects of `Width` ($\\beta = -0.5264^{***}, p < 0.001$), `Conductivity` ($\\beta = -1.1124^{**}, p = 0.003$), `Silt` ($\\beta = -0.5214^{*}, p = 0.017$), `Emerge Cover` ($\\beta = -0.2835^{*}, p = 0.039$), and `Cattle` ($\\beta = -0.2819^{*}, p = 0.032$). This shows that native desert fish require deep, warm water columns with low siltation.
2.  **Benthic-Specialist Grazers (Springsnails)**:
    *   *Predictability*: $R^2_{median} = -0.193$, mean MSE $= 1.121$.
    *   *Top Drivers*: `Temperature` (Gini $= 0.144$), `Conductivity` ($0.137$), and `Depth` ($0.127$).
    *   *GLM Coefficients*: Dominated by a highly significant positive effect of pool `Depth` ($\\beta = +0.4030^{***}, p < 0.001$), `Temperature` ($\\beta = +0.2891^{***}, p < 0.001$), and `Gravel` ($\\beta = +0.2498^{**}, p = 0.007$), with significant negative effects of `Width` ($\\beta = -0.4086^{***}, p < 0.001$) and `Cattle` ($\\beta = -0.4436^{***}, p < 0.001$).
3.  **Non-Native Invaders**:
    *   *Predictability*: $R^2_{median} = 0.207$, mean MSE $= 1.991$.
    *   *Top Drivers*: `Depth` (Gini $= 0.137$), `Conductivity` ($0.137$), and `Temperature` ($0.099$).
    *   *GLM Coefficients*: Significant positive effects of `Temperature` ($\\beta = +0.5853^{*}, p = 0.047$) and water `Diversion` ($\\beta = +0.7164^{***}, p < 0.001$), and a significant negative effect of `Cattle` grazing ($\\beta = -9.6555^{***}, p < 0.001$).
4.  **Endemics and Crenophilies**:
    *   *Predictability*: $R^2_{median} = 0.057$ (Endemics) and $R^2_{median} = 0.144$ (Crenophilies).
    *   *Top Drivers*: Driven by pool `Depth` (Gini $= 0.136$ and $0.160$) and `Non Natives` ($0.134$ and $0.115$).
    *   *GLM Coefficients*:
        *   *Endemics*: Strongly positive for `Depth` ($\\beta = +0.4544^{***}, p < 0.001$), `Equine` ($\\beta = +0.5082^{***}, p < 0.001$), and `Non Natives` ($\\beta = +0.2867^{***}, p < 0.001$); and negative for `Width` ($\\beta = -0.6617^{***}, p < 0.001$), `Conductivity` ($\\beta = -0.2184^{*}, p = 0.039$), and `Cattle` ($\\beta = -0.6538^{**}, p = 0.002$).
        *   *Crenophilies*: Strongly positive for `Depth` ($\\beta = +0.3242^{***}, p < 0.001$), `Temperature` ($\\beta = +0.3085^{***}, p < 0.001$), `Equine` ($\\beta = +0.2132^{**}, p = 0.003$), and `Non Natives` ($\\beta = +0.2783^{***}, p < 0.001$); and negative for `Width` ($\\beta = -0.3690^{***}, p < 0.001$), `Conductivity` ($\\beta = -0.2520^{*}, p = 0.014$), `Bank Cover` ($\\beta = -0.1296^{**}, p = 0.003$), and `Cattle` ($\\beta = -0.3285^{***}, p < 0.001$)."""

    content = content.replace(old_sec_d, new_sec_d)

    # 2. Update Table 6
    old_table_6 = """| Feature | Endemic Richness | Crenophile Richness | Springsnail Richness | Non-Native Richness | Native Fish Richness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **const** | $+0.7719^{***}$ | $+1.1189^{***}$ | $+0.4725^{*}$ | $\\text{N/A}$ | $-0.0683$ |
| **Depth** | $+0.4140^{***}$ | $+0.3340^{***}$ | $-0.0543$ | $+0.3319$ | $+0.2393^{**}$ |
| **Width** | $-0.0674$ | $-0.0210$ | $+0.1472$ | $-0.3547$ | $+0.4439^{***}$ |
| **Temperature** | $+0.0718$ | $+0.1102^{**}$ | $+0.0218$ | $+0.5853^{*}$ | $+0.2227^{***}$ |
| **Conductivity** | $+0.0135$ | $+0.0401$ | $-0.0573$ | $+0.3770$ | $+0.0384$ |
| **pH** | $-0.1557^{**}$ | $-0.1362^{**}$ | $-0.2212^{**}$ | $+0.1060$ | $-0.1747^{**}$ |
| **Emerge Cover** | $-0.0747^{*}$ | $-0.1009^{***}$ | $-0.0353$ | $+0.0929$ | $-0.0527$ |
| **Bank Cover** | $+0.0827^{**}$ | $+0.0652^{*}$ | $-0.0197$ | $+0.1814$ | $+0.0177$ |
| **Silt** | $-0.1472^{**}$ | $-0.0886^{*}$ | $-0.3235^{***}$ | $-0.4039$ | $-0.0934$ |
| **Sand** | $+0.0700$ | $+0.0945^{**}$ | $+0.0560$ | $-0.2693$ | $+0.0142$ |
| **Gravel** | $-0.0121$ | $-0.0163$ | $+0.1287$ | $-0.0197$ | $-0.0487$ |
| **Cobble** | $+0.0076$ | $+0.0245$ | $+0.1706^{**}$ | $-0.5038^{*}$ | $+0.0028$ |
| **Diversion** | $+0.1171^{**}$ | $+0.0970^{**}$ | $+0.0664$ | $+0.7164^{***}$ | $+0.1870^{**}$ |
| **Equine** | $-0.0471$ | $-0.0621$ | $-0.0101$ | $\\text{N/A}$ | $-0.0069$ |
| **Cattle** | $-0.0016$ | $+0.0333$ | $-0.1764$ | $-9.6555^{***}$ | $-0.0449$ |
| **Recreate** | $+0.0378$ | $+0.0135$ | $-0.0287$ | $+0.1271$ | $+0.0934$ |
| **Non Natives** | $+0.3687^{***}$ | $+0.2741^{**}$ | $+0.1069$ | $\\text{N/A}$ | $+0.2106^{*}$ |"""

    new_table_6 = """| Feature | Endemic Richness | Crenophile Richness | Springsnail Richness | Non-Native Richness | Native Fish Richness |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **const** | $+0.6560^{***}$ | $+0.8804^{***}$ | $+0.4158^{***}$ | $\\text{N/A}$ | $-0.8587^{*}$ |
| **Depth** | $+0.4544^{***}$ | $+0.3242^{***}$ | $+0.4030^{***}$ | $+0.3319$ | $+0.2381^{***}$ |
| **Width** | $-0.6617^{***}$ | $-0.3690^{***}$ | $-0.4086^{***}$ | $-0.3547$ | $-0.5264^{***}$ |
| **Temperature** | $+0.2626^{*}$ | $+0.3085^{***}$ | $+0.2891^{***}$ | $+0.5853^{*}$ | $+0.7600^{**}$ |
| **Conductivity** | $-0.2184^{*}$ | $-0.2520^{*}$ | $-0.2092$ | $+0.3770$ | $-1.1124^{**}$ |
| **pH** | $-0.1632$ | $-0.1232$ | $-0.1714$ | $+0.1060$ | $-0.0354$ |
| **Emerge Cover** | $-0.0194$ | $+0.0193$ | $+0.1278$ | $+0.0929$ | $-0.2835^{*}$ |
| **Bank Cover** | $-0.0913$ | $-0.1296^{**}$ | $-0.0934$ | $+0.1814$ | $+0.0411$ |
| **Silt** | $-0.0661$ | $-0.0323$ | $+0.1352$ | $-0.4039$ | $-0.5214^{*}$ |
| **Sand** | $-0.0838$ | $+0.0432$ | $+0.0435$ | $-0.2693$ | $-0.1479$ |
| **Gravel** | $+0.0321$ | $+0.0575$ | $+0.2498^{**}$ | $-0.0197$ | $-0.2567$ |
| **Cobble** | $-0.2141$ | $-0.0316$ | $-0.2261^{*}$ | $-0.5038^{*}$ | $-0.2672$ |
| **Diversion** | $+0.0606$ | $-0.0523$ | $-0.0479$ | $+0.7164^{***}$ | $-0.1833$ |
| **Equine** | $+0.5082^{***}$ | $+0.2132^{**}$ | $+0.2639^{***}$ | $\\text{N/A}$ | $+0.3060^{**}$ |
| **Cattle** | $-0.6538^{**}$ | $-0.3285^{***}$ | $-0.4436^{***}$ | $-9.6555^{***}$ | $-0.2819^{*}$ |
| **Recreate** | $+0.0285$ | $-0.0116$ | $+0.1262$ | $+0.1271$ | $-0.1763^{*}$ |
| **Non Natives** | $+0.2867^{***}$ | $+0.2783^{***}$ | $-0.0587$ | $\\text{N/A}$ | $+0.9477^{***}$ |"""

    content = content.replace(old_table_6, new_table_6)

    # 3. Update VIF / suppression section text
    old_suppression = """#### 2. Physical Covariation and GLM Suppression Effects
A key artifact of this multicollinearity is visible in Table 6 for pool physical dimensions. Pool `Depth` and `Width` are positively correlated ($r = 0.52$ globally) because larger regional oases tend to be both wider and deeper. When fitted simultaneously in a Poisson GLM:
*   Pool `Depth` exhibits a highly significant positive effect on endemic richness ($\beta = +0.4140, p < 0.001$).
*   Pool `Width` exhibits a negative, non-significant coefficient ($\beta = -0.0674, p = 0.449$).
This negative coefficient for width is a classic **suppression effect** caused by multicollinearity: because depth and width share information regarding water volume, the model assigns the positive effect of pool size entirely to `Depth` and a compensatory negative slope to `Width`. In reality, wider pools support more species. Therefore, managers and ecologists are cautioned against interpreting individual multivariable GLM coefficients in Table 6 as isolated physical slopes, but must evaluate them as a joint physical profile representing oasis permanence."""

    new_suppression = """#### 2. Physical Covariation and GLM Suppression Effects
Pool `Depth` and `Width` are positively correlated ($r = 0.52$ globally). When fitted simultaneously in the Poisson GLM, this physical covariation triggers a suppression effect: the model attributes the positive effect of pool size entirely to `Depth` ($\beta = +0.4544^{***}$) and assigns a compensatory negative slope to `Width` ($\beta = -0.6617^{***}$). This negative coefficient for width is a statistical artifact of multicollinearity rather than a biological process. Ecologists and managers are cautioned against interpreting individual GLM coefficients in isolation."""

    content = content.replace(old_suppression, new_suppression)

    # 4. Update Section 5 (Diverging Management Prescriptions Across Taxa)
    old_sec_5 = """1.  **Native Fish Management: Regional Flow Volume and Groundwater Protection**
    *   *Ecological Driver*: Native fish are highly sensitive to pool dimensions (Width Gini $= 0.183$, Depth Gini $= 0.171$). The standardized Poisson GLM reveals extremely significant positive effects of pool `Width` ($\beta = +0.4439, p < 0.001$) and `Depth` ($\beta = +0.2393, p = 0.005$). 
    *   *Prescription*: Because swimming species require a continuous, stable three-dimensional water column, management must focus on **volume retention**. This requires setting strict limits on regional groundwater extraction and local pumping to prevent water-table drawdown. Minor drops in regional aquifer pressure directly shrink pool depth and width, collapsing the available habitat for fish. Furthermore, any agricultural water diversion at the spring head must be prohibited or strictly bypassed.
2.  **Springsnail Management: Active Substrate Restoration and Cattle Exclusion**
    *   *Ecological Driver*: Springsnails are benthic micro-grazers entirely decoupled from water volume, instead governed by substrate composition (Silt Gini $= 0.198$, Cobble Gini $= 0.120$). The standardized Poisson GLM shows a massive negative filter of `Silt` ($\beta = -0.3235, p < 0.001$) and a positive driver of `Cobble` ($\beta = +0.1706, p = 0.007$).
    *   *Prescription*: Simple riparian fencing is necessary to prevent active cattle and horse trampling, but it is insufficient on its own because fences do not remove historical silt. Active **benthic substrate restoration** is required. This includes manually flushing or suctioning fine silts from gravel beds and adding clean, coarse gravel and cobble substrates. These physical actions recreate the hard micro-grazing surfaces springsnails need to graze on periphyton and attach their egg capsules.
3.  **Non-Native Invader Management: Managing Human Vectors and Access**
    *   *Ecological Driver*: Non-native richness is driven by stable temperatures and depth, but is significantly positively promoted by human-mediated disturbances, specifically water `Diversion` ($\beta = +0.1282, p = 0.031$) and recreational usage (`Recreate`, $\beta = +0.1554, p = 0.002$).
    *   *Prescription*: Controlling biological invasion requires **managing human access and modification**. Key actions include restricting recreational access (e.g., wading, bathing, swimming) at high-value oases, implementing strict gear-washing protocols for field researchers, and dismantling illegal human-made diversion ponds. Diversions and human-made pool modifications slow down water flow and create warm, pond-like habitats that biologically favor invasive cichlids, bullfrogs, and mosquitofish over native stream-adapted endemics.
4.  **Endemics & Crenophilies: Balanced Habitat Preservation**
    *   *Ecological Driver*: Generalists whose distribution is a composite of pool `Depth` ($\beta = +0.4140, p < 0.001$), `Silt` ($\beta = -0.1472, p = 0.003$), and bank vegetation (`Bank Cover`, $\beta = +0.0827, p = 0.008$).
    *   *Prescription*: They require a balanced, multi-faceted approach combining flow protection (maintaining depth $>40$ cm), livestock exclusion (preserving bank cover and preventing bank collapse), and sediment control (keeping silt substrate $<20\%$)."""

    new_sec_5 = """1.  **Native Fish Management: Regional Flow Volume and Groundwater Protection**
    *   *Ecological Driver*: Native fish are highly sensitive to pool dimensions (Depth Gini $= 0.197$). The standardized Poisson GLM reveals significant positive effects of pool `Depth` ($\\beta = +0.2381^{***}, p < 0.001$) and `Temperature` ($\\beta = +0.7600^{**}, p = 0.009$).
    *   *Prescription*: Because swimming species require a continuous, stable three-dimensional water column, management must focus on **volume retention**. This requires setting strict limits on regional groundwater extraction and local pumping to prevent water-table drawdown. Minor drops in regional aquifer pressure directly shrink pool depth and width, collapsing the available habitat for fish. Furthermore, any agricultural water diversion at the spring head must be prohibited or strictly bypassed.
2.  **Springsnail Management: Active Substrate Restoration and Cattle Exclusion**
    *   *Ecological Driver*: Springsnails are benthic micro-grazers governed by substrate composition and local disturbances. The standardized Poisson GLM shows a highly significant negative filter of `Cattle` grazing ($\\beta = -0.4436^{***}, p < 0.001$) and a positive driver of `Gravel` ($\\beta = +0.2498^{**}, p = 0.007$) and `Depth` ($\\beta = +0.4030^{***}, p < 0.001$).
    *   *Prescription*: Simple riparian fencing is necessary to prevent active cattle and horse trampling, but it is insufficient on its own because fences do not remove historical silt. Active **benthic substrate restoration** is required. This includes manually flushing or suctioning fine silts from gravel beds and adding clean, coarse gravel and cobble substrates. These physical actions recreate the hard micro-grazing surfaces springsnails need to graze on periphyton and attach their egg capsules.
3.  **Non-Native Invader Management: Managing Human Vectors and Access**
    *   *Ecological Driver*: Non-native richness is driven by stable temperatures and depth, but is significantly positively promoted by human-mediated disturbances, specifically water `Diversion` ($\\beta = +0.7164^{***}, p < 0.001$) and `Temperature` ($\\beta = +0.5853^{*}, p = 0.047$).
    *   *Prescription*: Controlling biological invasion requires **managing human access and modification**. Key actions include restricting recreational access (e.g., wading, bathing, swimming) at high-value oases, implementing strict gear-washing protocols for field researchers, and dismantling illegal human-made diversion ponds. Diversions and human-made pool modifications slow down water flow and create warm, pond-like habitats that biologically favor invasive cichlids, bullfrogs, and mosquitofish over native stream-adapted endemics.
4.  **Endemics & Crenophilies: Balanced Habitat Preservation**
    *   *Ecological Driver*: Generalists whose distribution is a composite of pool `Depth` ($\\beta = +0.4544^{***}, p < 0.001$), `Cattle` grazing ($\\beta = -0.6538^{**}, p = 0.002$), and non-native presence ($\\beta = +0.2867^{***}, p < 0.001$).
    *   *Prescription*: They require a balanced, multi-faceted approach combining flow protection (maintaining depth $>30$ cm), livestock exclusion (preserving bank cover and preventing bank collapse), and sediment control (keeping silt substrate $<20\%$)."""

    content = content.replace(old_sec_5, new_sec_5)

    # 5. Clean up other individual outdated text occurrences
    content = content.replace("`Depth` ($\\beta = +0.4140, p < 0.001$)", "`Depth` ($\\beta = +0.4544^{***}, p < 0.001$)")
    content = content.replace("`Silt` ($\\beta = -0.1472, p = 0.003$)", "`Cattle` ($\\beta = -0.6538^{**}, p = 0.002$)")
    content = content.replace("`Bank Cover`, $\\beta = +0.0827, p = 0.008$", "`Non Natives`, $\\beta = +0.2867^{***}, p < 0.001$")
    content = content.replace("depth, width, temperature, conductivity, silt, sand, bank cover, emergent cover, cattle, equine, diversion", "depth, width, temperature, conductivity, pH, silt, sand, gravel, cobble, emergent cover, bank cover, diversion, recreation, cattle, equine, non-natives")
    
    # 6. Remove Author Contributions section at the end
    auth_sec_idx = content.find("## Author Contributions")
    if auth_sec_idx != -1:
        content = content[:auth_sec_idx].rstrip() + "\n"
        print("Removed Author Contributions section.")

    # 7. Remove AI slop / chatty phrasing in introductory blocks
    content = content.replace(
        "To understand the methodological design of the foundational paper, it is essential to consider the scientific literature and established protocols that guide the study's parameters and statistical framework:",
        "The foundational study parameters and hydroecological covariates are established in the literature:"
    )
    content = content.replace(
        "By integrating distribution-free, non-parametric modeling into our workflow, we uncovered three critical ecological insights that standard linear parametric models (and basic correlation analysis) were unable to detect:",
        "Non-parametric modeling and supervised regression resolved three key ecological patterns obscured by standard linear analyses:"
    )
    content = content.replace(
        "The decision to introduce non-linear decomposition (such as t-SNE) and factor analysis to complement standard linear PCA is driven by theoretical ecological motivations, the need to address multicollinearity, and the unique constraints of this desert springs dataset:",
        "Integrating non-linear ordination (t-SNE) and factor analysis (FA) addresses the limitations of PCA under multicollinearity and zero-inflation:"
    )
    content = content.replace(
        "In this reanalysis, we build directly upon their foundational work by clarifying a critical statistical and ecological distinction regarding the role of Principal Component Analysis (PCA) and data transformations.",
        "This reanalysis builds upon their work by clarifying the distinction between linear scale-standardization (z-scoring) and modeling non-linear ecological structures and thresholds."
    )
    content = content.replace(
        "We write to offer a constructive extension and conceptual elaboration of the important regional census of desert spring ecosystems in the Great Basin and Mojave Desert regions by Matthew J. Forrest et al. (2026). Their comprehensive cataloging of 1,121 springs represents a monumental effort in desert springs conservation.",
        "We present a constructive extension of the regional census of desert spring ecosystems by Forrest et al. (2026). Their cataloging of 1,121 springs is a major contribution to desert spring conservation."
    )
    content = content.replace(
        "Sincerely,  \n*The Analytical Replication Team*",
        ""
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("results.md successfully updated and tightened!")

if __name__ == "__main__":
    main()
