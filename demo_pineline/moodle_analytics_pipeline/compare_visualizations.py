#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare Real vs Simulated Visualizations
========================================
Opens both cluster visualizations side-by-side for comparison
"""

import os
import subprocess
import sys
from pathlib import Path


def open_image(path: str):
    """Open image using default application"""
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['open', path])
    elif sys.platform == 'win32':  # Windows
        os.startfile(path)
    else:  # Linux
        subprocess.run(['xdg-open', path])


def main():
    print("\n" + "="*80)
    print("CLUSTER VISUALIZATION COMPARISON")
    print("="*80)
    
    # Paths
    real_viz = Path('outputs/clustering/cluster_visualization.png')
    sim_viz = Path('outputs/simulation/simulated_cluster_visualization.png')
    
    # Check files exist
    if not real_viz.exists():
        print("\n❌ Real data visualization not found!")
        print(f"   Expected: {real_viz}")
        print("   Run the pipeline first: python main.py")
        return
    
    if not sim_viz.exists():
        print("\n❌ Simulated data visualization not found!")
        print(f"   Expected: {sim_viz}")
        print("   Run the pipeline first: python main.py")
        return
    
    print("\n✅ Both visualizations found!")
    print(f"   Real:      {real_viz}")
    print(f"   Simulated: {sim_viz}")
    
    # Open both
    print("\n🖼️  Opening visualizations...")
    try:
        open_image(str(real_viz))
        open_image(str(sim_viz))
        print("✅ Visualizations opened!")
    except Exception as e:
        print(f"❌ Error opening images: {e}")
        print(f"\n💡 Manually open:")
        print(f"   {real_viz.absolute()}")
        print(f"   {sim_viz.absolute()}")
        return
    
    # Comparison guide
    print("\n" + "="*80)
    print("📊 COMPARISON CHECKLIST")
    print("="*80)
    print("""
Compare the two visualizations and check:

Visual Similarity:
  □ Similar cluster shapes and positions?
  □ Similar cluster sizes (number of points)?
  □ Similar spread/density within clusters?
  □ Similar separation between clusters?

Quality Indicators:
  □ No extreme outliers in simulated data?
  □ Clusters don't overlap too much?
  □ Distribution looks natural (not too uniform)?
  □ Variance explained similar between both?

If most boxes checked ✅:
  → Simulation quality is GOOD!
  
If many boxes unchecked ❌:
  → Consider adjusting simulation parameters:
     - Reduce noise level (e.g., 0.05 instead of 0.1)
     - Increase number of simulated students
     - Check cluster statistics quality
""")
    
    print("="*80)
    print("💡 TIP: For detailed similarity metrics, check:")
    print("   outputs/cluster_comparison/cluster_comparison_report.txt")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
