import os
import shutil
import subprocess

def run_script(script_name):
    print(f"Running {script_name}...")
    res = subprocess.run(["./venv/bin/python", script_name], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR running {script_name}:")
        print(res.stderr)
        raise Exception(f"Failed to execute {script_name}")
    print(res.stdout)

def main():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    brain_dir = os.path.expanduser("~/.gemini/antigravity-ide/brain/48f3837e-25a5-48b3-9936-68a043785b65")
    sync_to_brain = os.path.isdir(brain_dir)
    
    # 1. Clean up old figure files in workspace figures/
    workspace_figs = os.path.join(workspace_dir, "figures")
    os.makedirs(workspace_figs, exist_ok=True)
    
    print("Cleaning up old figure files in workspace figures/...")
    for f in os.listdir(workspace_figs):
        # We delete anything in figures/ that doesn't start with Figure_1 to Figure_16 or Figure_S1 to Figure_S5
        # or we just clear the directory to ensure only fresh files are present.
        # Clearing and rebuilding is the most robust way to remove all duplicates!
        fpath = os.path.join(workspace_figs, f)
        if os.path.isfile(fpath):
            os.remove(fpath)
            
    if sync_to_brain:
        brain_figs = os.path.join(brain_dir, "figures")
        os.makedirs(brain_figs, exist_ok=True)
        print("Cleaning up old figure files in brain figures/...")
        for f in os.listdir(brain_figs):
            fpath = os.path.join(brain_figs, f)
            if os.path.isfile(fpath):
                os.remove(fpath)
            
    # 2. Execute all Python scripts in sequence
    scripts = [
        "generate_tables.py",
        "recreate_analysis.py",
        "unsupervised_analysis.py",
        "discover_latent_patterns.py",
        "analyze_all_aquifers.py",
        "non_parametric_analysis.py",
        "taxa_regression_analysis.py",
        "visualize_sites_clustermap.py",
        "visualize_cooccurrence.py",
        "visualize_tsne_grid.py"
    ]
    
    for s in scripts:
        run_script(s)
        
    # 3. Verify generated figures in workspace figures/
    print("\nVerifying generated figures in workspace figures/:")
    generated_files = sorted(os.listdir(workspace_figs))
    for gf in generated_files:
        print(f"  {gf}")
        
    # 4. Copy all new figures and excel sheets to the brain artifacts directory
    print("\nCopying new figure files to brain figures/...")
    for f in os.listdir(workspace_figs):
        src = os.path.join(workspace_figs, f)
        dst = os.path.join(brain_figs, f)
        shutil.copy2(src, dst)
        
    print("Copying Excel spreadsheets and results to brain root...")
    excel_files = [
        "Table_1_Group_Statistics.xlsx",
        "Table_2_Kruskal_Wallis.xlsx",
        "Table_3_Spearman_Correlations.xlsx",
        "Table_4_Bootstrap_Performance.xlsx",
        "Table_5_Partial_Dependence.xlsx",
        "Table_6_Taxa_Regression.xlsx",
        "Data_Table_S5.xlsx"
    ]
    for ef in excel_files:
        src = os.path.join(workspace_dir, ef)
        dst = os.path.join(brain_dir, ef)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  Copied {ef}")
            
    # Copy walkthrough.md back to brain root to keep them in sync
    walkthrough_src = os.path.join(workspace_dir, "walkthrough.md")
    walkthrough_dst = os.path.join(brain_dir, "walkthrough.md")
    if os.path.exists(walkthrough_src):
        shutil.copy2(walkthrough_src, walkthrough_dst)
        print("  Synced walkthrough.md to brain root")
            
    # 5. Compile final HTML publication
    run_script("render_publication.py")
    
    print("\nPipeline execution, cleanup, and sync completed successfully!")

if __name__ == "__main__":
    main()
