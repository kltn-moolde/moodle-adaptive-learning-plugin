# Quick Reference: All Visualizations

## 📊 Complete Visualization Output

Pipeline generates **11 visualizations** across 4 categories:

---

## 1️⃣ Feature Extraction (outputs/features/)

*No visualizations* - Data only

---

## 2️⃣ Clustering Analysis (outputs/clustering/)

### `optimal_k_analysis.png`
- **Elbow curve** - Find optimal number of clusters
- **Silhouette scores** - Cluster quality metrics
- **Davies-Bouldin index** - Separation metrics

### `cluster_visualization.png`
- **PCA scatter plot** of REAL student clusters
- Color-coded by cluster
- Explained variance shown

### `cluster_profiles.png`
- **Radar charts** for each cluster
- Shows feature characteristics per cluster
- Helps understand what makes each cluster unique

---

## 3️⃣ Data Simulation (outputs/simulation/)

### `simulated_cluster_visualization.png` ⭐ NEW
- **PCA scatter plot** of SIMULATED student clusters
- Same style as real data visualization
- Compare side-by-side with real data

---

## 4️⃣ Feature Comparison (outputs/comparison/)

### `distribution_comparison.png`
- **Histogram overlays** for top features
- Real (blue) vs Simulated (orange)
- KS test p-values shown

### `cluster_proportion_comparison.png`
- **Bar chart** comparing cluster sizes
- Real vs Simulated proportions
- Chi-square test results

### `comparison_dashboard.png`
- **9-panel comprehensive view**
- Feature distributions (6 panels)
- Cluster proportions (1 panel)
- Statistical summaries (2 panels)

---

## 5️⃣ Cluster Comparison (outputs/cluster_comparison/)

### `cluster_pca_comparison.png`
- **Side-by-side PCA plots**
- Real data (left) vs Simulated data (right)
- Direct visual comparison

### `cluster_sizes_comparison.png`
- **Bar chart** with exact student counts
- Real (blue) vs Simulated (orange)
- Shows distribution differences

### `cluster_profiles_comparison.png`
- **Overlaid radar charts** per cluster
- Real (blue line) vs Simulated (orange line)
- Shows feature-level similarity

### `feature_distributions_comparison.png`
- **Histogram overlays** for top 6 features
- Density normalized
- Visual distribution matching

### `similarity_metrics_dashboard.png`
- **Gauge meter** for overall similarity score
- **Bar charts** for individual metrics
- **Distance metrics** visualization
- Complete metrics overview

---

## 📁 Quick Access

### View All Real Data Visualizations
```bash
open outputs/clustering/*.png
```

### View All Simulated Data Visualizations
```bash
open outputs/simulation/*.png
```

### View All Comparison Visualizations
```bash
open outputs/comparison/*.png
open outputs/cluster_comparison/*.png
```

### Compare Real vs Simulated
```bash
python compare_visualizations.py
```

---

## 🎯 Usage Guide

### For Quick Check
1. `cluster_visualization.png` - Real data
2. `simulated_cluster_visualization.png` - Simulated data
3. Compare visually

### For Deep Analysis
1. `cluster_pca_comparison.png` - Side-by-side PCA
2. `cluster_profiles_comparison.png` - Feature comparison
3. `similarity_metrics_dashboard.png` - Quantitative metrics

### For Presentations
1. `optimal_k_analysis.png` - Show methodology
2. `cluster_visualization.png` - Show results
3. `simulated_cluster_visualization.png` - Show simulation
4. `similarity_metrics_dashboard.png` - Show validation

### For Reports
Include all 11 visualizations with captions

---

## 💡 Interpretation Tips

### Good Simulation Indicators
✅ `cluster_pca_comparison.png` shows similar patterns  
✅ `cluster_sizes_comparison.png` shows similar proportions  
✅ `cluster_profiles_comparison.png` shows overlapping lines  
✅ `similarity_metrics_dashboard.png` shows score ≥ 80%

### Warning Signs
⚠️ Very different cluster shapes in PCA  
⚠️ Large differences in cluster sizes  
⚠️ Radar charts don't overlap  
⚠️ Similarity score < 70%

---

## 🔍 File Sizes (Approximate)

| Category | Files | Total Size |
|----------|-------|------------|
| Clustering | 3 PNG | ~2 MB |
| Simulation | 1 PNG | ~350 KB |
| Comparison | 3 PNG | ~1.5 MB |
| Cluster Comparison | 5 PNG | ~3 MB |
| **TOTAL** | **12 files** | **~7 MB** |

---

## 🎨 Color Schemes

### Cluster Colors
- **Viridis colormap** - Blue to yellow gradient
- Consistent across all visualizations
- Colorblind-friendly

### Comparison Colors
- **Real data**: Steel blue (#4682B4)
- **Simulated data**: Coral (#FF7F50)
- High contrast for easy distinction

---

## 📊 Resolution & Quality

All visualizations saved at:
- **DPI**: 300 (publication quality)
- **Format**: PNG (transparent background)
- **Size**: Optimized for reports and presentations

---

## 🚀 Automation

```python
# All visualizations generated automatically
python main.py

# Output summary
print(f"Generated visualizations:")
print(f"  Clustering:        3 files")
print(f"  Simulation:        1 file")
print(f"  Comparison:        3 files")
print(f"  Cluster Comparison: 5 files")
print(f"  Total:            12 files")
```

---

**Last Updated**: October 30, 2025  
**Total Visualizations**: 12  
**Total File Size**: ~7 MB  
**Generation Time**: ~30-60 seconds
