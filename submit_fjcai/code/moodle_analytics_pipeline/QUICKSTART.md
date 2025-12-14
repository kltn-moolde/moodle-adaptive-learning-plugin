# Quick Start Guide - GMM-Based Pipeline

## 🚀 Get Started in 5 Minutes

### Step 1: Installation

```bash
cd demo_pineline/moodle_analytics_pipeline
pip install -r requirements.txt
```

### Step 2: Run Pipeline

```bash
python main.py
```

Done! Pipeline sẽ tự động:
1. Extract features từ data
2. Select optimal features
3. Find optimal number of clusters
4. Generate synthetic data using GMM
5. Validate and compare results

---

## 📊 Check Results

After running, check `outputs/` directory:

```bash
outputs/
├── features/                    # ✅ Extracted features
├── feature_selection/           # ✅ Selected features + analysis
├── optimal_clusters/            # ✅ Optimal k + evaluation plots
├── gmm_generation/              # ✅ Synthetic data + comparison
└── validation/                  # ✅ Quality report + metrics
```

### Key Files to Check:

1. **Feature Selection Report**:
   ```bash
   cat outputs/feature_selection/feature_selection_report.txt
   ```

2. **Optimal Clusters Report**:
   ```bash
   cat outputs/optimal_clusters/optimal_clusters_report.txt
   ```

3. **Validation Report**:
   ```bash
   cat outputs/validation/validation_report.txt
   ```

---

## 🎯 Expected Output

### Console Output Example:

```
================================================================================
MOODLE ANALYTICS PIPELINE - GMM-BASED EXECUTION
================================================================================

📊 PHASE 1: Feature Extraction
--------------------------------------------------------------------------------
✓ Loaded 150 real students with 25 features

🔍 PHASE 2: Feature Selection (Variance + Correlation Filtering)
--------------------------------------------------------------------------------
  ✓ Retained: 18 features (variance filter)
  ✗ Removed: 7 low-variance features
  ✓ Retained: 15 features (correlation filter)
  ✗ Removed: 3 highly-correlated features
✅ SELECTED 15 OPTIMAL FEATURES

🎯 PHASE 3: Finding Optimal Number of Clusters (GMM)
--------------------------------------------------------------------------------
Testing k from 2 to 10...
Evaluating k=2... BIC: 1245.67, Silhouette: 0.523
Evaluating k=3... BIC: 1156.34, Silhouette: 0.612
Evaluating k=4... BIC: 1189.45, Silhouette: 0.587
...
🎯 OPTIMAL K: 3
   BIC: 1156.34
   Silhouette: 0.612

🔮 PHASE 4: GMM Data Generation
--------------------------------------------------------------------------------
✓ Generated 200 synthetic students
  Cluster distribution:
    Cluster 0 ('giỏi'): 65 (32.5%)
    Cluster 1 ('khá'): 75 (37.5%)
    Cluster 2 ('yếu'): 60 (30.0%)

✅ PHASE 5: Validation (Real vs Synthetic)
--------------------------------------------------------------------------------
Validating 15 features...
  total_events                   - KS p-value: 0.1234 (✓)
  mean_module_grade              - KS p-value: 0.0987 (✓)
  viewed                         - KS p-value: 0.2145 (✓)
  ...
🎯 OVERALL QUALITY SCORE: 87.3% (Excellent)
   Synthetic data very closely matches real data distribution

================================================================================
✅ PIPELINE COMPLETED SUCCESSFULLY!
================================================================================

📊 PIPELINE SUMMARY (GMM-BASED)
================================================================================
Real students:        150
Synthetic students:   200
Optimal clusters (k): 3
Features extracted:   25
Features selected:    15

🎯 QUALITY ANALYSIS
Overall Score:        87.3%
Grade:                Excellent
Quality:              Synthetic data very closely matches real data distribution

KS Tests Passed:      14/15 (93.3%)

✅ All outputs saved to 'outputs/' directory
================================================================================
```

---

## 🎨 Visualizations Generated

### 1. Feature Selection Analysis
![Feature Selection](outputs/feature_selection/feature_selection_analysis.png)
- Top features by importance
- Variance distribution
- Correlation heatmap
- Selection summary

### 2. Optimal Clusters Evaluation
![Optimal Clusters](outputs/optimal_clusters/optimal_clusters_evaluation.png)
- BIC curve (lower is better)
- AIC curve (lower is better)
- Silhouette score (higher is better)
- Composite score

### 3. Real vs Synthetic Comparison
![PCA Comparison](outputs/gmm_generation/real_vs_synthetic_pca.png)
- PCA visualization of clusters
- Distribution comparison
- Correlation matrices

### 4. Validation Results
![KS Tests](outputs/validation/ks_test_results.png)
- KS test p-values for each feature
- Distribution box plots
- Statistical comparison

---

## ⚙️ Customization Examples

### Example 1: Change Number of Synthetic Students

```python
from core import MoodleAnalyticsPipeline

pipeline = MoodleAnalyticsPipeline()
results = pipeline.run_full_pipeline(
    grades_path='../data/grades.csv',
    logs_path='../data/logs.csv',
    n_synthetic_students=500  # ← Change this
)
```

### Example 2: Adjust Feature Selection Thresholds

```python
results = pipeline.run_full_pipeline(
    grades_path='../data/grades.csv',
    logs_path='../data/logs.csv',
    variance_threshold=0.02,      # ← Stricter (more filtering)
    correlation_threshold=0.90,   # ← Stricter (remove more redundant)
    max_features=10              # ← Limit to top 10
)
```

### Example 3: Test Different K Range

```python
results = pipeline.run_full_pipeline(
    grades_path='../data/grades.csv',
    logs_path='../data/logs.csv',
    k_range=range(3, 8)  # ← Only test k=3 to k=7
)
```

### Example 4: Use Only Selected Modules

```python
from core import FeatureSelector, OptimalClusterFinder
import pandas as pd
import json

# Load features
with open('outputs/features/features_scaled.json', 'r') as f:
    features = pd.DataFrame(json.load(f))

# Select features
selector = FeatureSelector(variance_threshold=0.01)
selected = selector.process_pipeline(features, 'outputs/feature_selection')

# Find optimal clusters
finder = OptimalClusterFinder(k_range=range(2, 8))
optimal_k, gmm = finder.process_pipeline(
    X=features[selected].values,
    output_dir='outputs/optimal_clusters'
)

print(f"Optimal K: {optimal_k}")
```

---

## 🔍 Understanding Results

### Quality Score Interpretation

| Score Range | Grade      | Interpretation |
|-------------|------------|----------------|
| 85-100%     | Excellent  | Synthetic data rất giống real data |
| 70-84%      | Good       | Synthetic data tương đối giống với minor differences |
| 50-69%      | Fair       | Synthetic data có moderate similarity |
| <50%        | Poor       | Synthetic data khác biệt đáng kể |

### KS Test Results

- **p-value > 0.05**: ✓ PASS - Distributions are similar
- **p-value ≤ 0.05**: ✗ FAIL - Distributions differ significantly

**Pass Rate**: Số features pass / Total features

### Optimal K Selection

Pipeline tự động chọn k dựa trên:
- **50% BIC score** (normalized, inverted)
- **50% Silhouette score** (normalized)

K với composite score cao nhất sẽ được chọn.

---

## 🐛 Troubleshooting

### Issue 1: "No features passed variance threshold"

**Solution**: Lower variance_threshold
```python
variance_threshold=0.001  # Instead of 0.01
```

### Issue 2: "Quality score too low (<50%)"

**Possible causes**:
- Data có nhiều noise
- Features không representative
- K không optimal

**Solutions**:
1. Increase k_range: `k_range=range(2, 15)`
2. Adjust feature selection thresholds
3. Check input data quality

### Issue 3: "ImportError: No module named 'sklearn'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 4: Pipeline runs but no outputs

**Check**:
```python
import os
print(os.path.exists('outputs'))  # Should be True
```

**Fix**:
```python
pipeline = MoodleAnalyticsPipeline(base_output_dir='./outputs')
```

---

## 📝 Next Steps

1. **Review Validation Report**:
   - Check KS test pass rate
   - Review distribution comparisons
   - Examine correlation similarity

2. **Analyze Visualizations**:
   - Feature selection analysis
   - Optimal clusters evaluation
   - Real vs synthetic comparison

3. **Adjust Parameters**:
   - Fine-tune thresholds based on results
   - Test different k ranges
   - Experiment with feature selection

4. **Use Synthetic Data**:
   - Load from `outputs/gmm_generation/synthetic_students_gmm.csv`
   - Use for testing, simulation, or augmentation

---

## 📚 Additional Resources

- **README_GMM.md**: Full documentation
- **MODULE_SUMMARY.md**: Detailed module docs
- **METRICS_GUIDE.md**: Metrics explanation
- **config.py**: All configurable parameters

---

## 🤝 Need Help?

- Check logs in `pipeline.log`
- Review error messages in console
- Inspect intermediate outputs in `outputs/` subdirectories

---

**Happy Analyzing! 🎉**
