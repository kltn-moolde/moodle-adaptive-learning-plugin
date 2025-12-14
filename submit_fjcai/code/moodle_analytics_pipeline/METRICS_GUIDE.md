# Similarity Metrics Guide

## Overview

Module này sử dụng nhiều metrics khác nhau để đánh giá độ tương đồng giữa real data và simulated data. Document này giải thích chi tiết từng metric.

---

## 📊 Cluster Quality Metrics

### 1. Silhouette Score

**Range**: -1 to 1 (Higher is better)

**What it measures**: 
- How well-separated clusters are
- Combination of cohesion (within-cluster) and separation (between-cluster)

**Interpretation**:
- **0.7 - 1.0**: Strong structure, well-separated clusters
- **0.5 - 0.7**: Reasonable structure
- **0.25 - 0.5**: Weak structure, overlapping clusters
- **< 0.25**: No substantial cluster structure

**Formula**:
```
s(i) = (b(i) - a(i)) / max(a(i), b(i))

where:
  a(i) = average distance to points in same cluster
  b(i) = average distance to points in nearest different cluster
```

**In Comparison**:
- Compare silhouette scores of real vs simulated
- Smaller difference = Better similarity
- Ideal: Both scores in same range (e.g., both 0.5-0.7)

---

### 2. Davies-Bouldin Index

**Range**: 0 to ∞ (Lower is better)

**What it measures**:
- Average similarity ratio between each cluster and its most similar cluster
- Lower values indicate better cluster separation

**Interpretation**:
- **< 0.5**: Excellent separation
- **0.5 - 1.0**: Good separation
- **1.0 - 2.0**: Acceptable separation
- **> 2.0**: Poor separation, overlapping clusters

**Formula**:
```
DB = (1/k) * Σ max(R_ij)

where:
  R_ij = (S_i + S_j) / d_ij
  S_i = average distance from points in cluster i to centroid
  d_ij = distance between cluster i and j centroids
```

**In Comparison**:
- Lower difference = More similar cluster structures
- Both should be in similar ranges

---

### 3. Calinski-Harabasz Score (Variance Ratio)

**Range**: 0 to ∞ (Higher is better)

**What it measures**:
- Ratio of between-cluster dispersion to within-cluster dispersion
- Higher values mean clusters are dense and well-separated

**Interpretation**:
- **> 1000**: Excellent clustering
- **500 - 1000**: Very good
- **100 - 500**: Good
- **< 100**: Weak clustering

**Formula**:
```
CH = (SSB / SSW) * ((n - k) / (k - 1))

where:
  SSB = Sum of squares between clusters
  SSW = Sum of squares within clusters
  n = number of samples
  k = number of clusters
```

**In Comparison**:
- Higher absolute values indicate better-defined clusters
- Smaller difference = More similar quality

---

## 📐 Distance-Based Metrics

### 4. Cluster Center Distance

**Range**: 0 to ∞ (Lower is better)

**What it measures**:
- Euclidean distance between cluster centroids of real vs simulated
- How similar are the "typical" students in each cluster

**Interpretation**:
- **< 0.5**: Very similar cluster centers
- **0.5 - 1.0**: Somewhat similar
- **1.0 - 2.0**: Moderately different
- **> 2.0**: Very different

**Calculation**:
```python
# For each real cluster, find closest simulated cluster
distances = cdist(real_centers, sim_centers, metric='euclidean')
min_distances = distances.min(axis=1)
mean_distance = min_distances.mean()
```

**In Comparison**:
- Measures "location" similarity in feature space
- Normalized features → distances are comparable

---

### 5. Wasserstein Distance (Earth Mover's Distance)

**Range**: 0 to ∞ (Lower is better)

**What it measures**:
- Minimum "work" to transform one distribution into another
- Used for cluster size distributions and feature distributions

**Interpretation for Cluster Sizes**:
- **< 0.05**: Nearly identical distributions
- **0.05 - 0.1**: Very similar
- **0.1 - 0.2**: Somewhat similar
- **> 0.2**: Different distributions

**Intuition**:
- Imagine distributions as piles of dirt
- Distance = effort to reshape one pile into another
- Accounts for both location and amount differences

**Example**:
```
Real clusters:      [30%, 25%, 20%, 15%, 10%]
Simulated clusters: [28%, 27%, 18%, 17%, 10%]
→ Small Wasserstein distance (similar distributions)

Real clusters:      [50%, 30%, 10%, 5%, 5%]
Simulated clusters: [20%, 20%, 20%, 20%, 20%]
→ Large Wasserstein distance (very different)
```

---

## 🎯 Overall Similarity Score

**Range**: 0 to 100 (Higher is better)

**What it measures**:
- Weighted combination of all metrics
- Single score summarizing overall similarity

**Components** (weighted equally):
1. **Silhouette similarity**: `1 - (|real_sil - sim_sil| / 2) * 100`
2. **Center distance**: `max(0, 1 - mean_distance/10) * 100`
3. **Distribution similarity**: `max(0, 1 - wasserstein) * 100`
4. **Feature similarity**: `max(0, 1 - mean_feat_dist/5) * 100`

**Grading Scale**:
```
90-100%: A+ / A   → Excellent
80-89%:  A- / B+  → Very Good
70-79%:  B / B-   → Good
60-69%:  C+ / C   → Fair
50-59%:  D+       → Moderate
< 50%:   D / F    → Poor
```

**Interpretation**:
- **A (90-100%)**: Simulation captures nearly all patterns
  - Use for privacy-preserving sharing
  - Suitable for ML training
  
- **B (80-89%)**: Strong similarity
  - Good for research
  - Minor edge case differences
  
- **C (70-79%)**: Acceptable similarity
  - Check if good enough for your use case
  - May need parameter tuning
  
- **D-F (< 70%)**: Needs improvement
  - Review simulation parameters
  - Check feature quality
  - May need more real data

---

## 📈 Feature Distribution Similarity

**Per-feature Wasserstein distances**

**What it measures**:
- How similar each feature's distribution is between real and simulated

**Interpretation per feature**:
- **< 0.1**: Nearly identical
- **0.1 - 0.3**: Similar
- **0.3 - 0.5**: Somewhat different
- **> 0.5**: Very different

**Use cases**:
- Identify which features are well-simulated
- Find features that need better simulation
- Prioritize features for improvement

---

## 🔍 How to Use These Metrics

### 1. First Look: Overall Similarity Score
```python
if score >= 80:
    print("✅ Simulation quality is good!")
elif score >= 60:
    print("⚠️  Acceptable, but could be improved")
else:
    print("❌ Needs improvement")
```

### 2. Diagnose Issues

**If score is low, check**:

- **Silhouette/Davies-Bouldin very different?**
  - → Cluster quality mismatch
  - → Try different noise level
  
- **High cluster center distance?**
  - → Centroids are in wrong locations
  - → Check cluster statistics quality
  
- **High Wasserstein distance?**
  - → Distribution shapes differ
  - → Review simulation strategy
  
- **Specific features have high distance?**
  - → Those features poorly simulated
  - → May need feature-specific noise

### 3. Iterative Improvement

```python
# Try different noise levels
for noise in [0.05, 0.1, 0.15, 0.2]:
    simulate_data(noise_level=noise)
    metrics = compare_clusters()
    print(f"Noise {noise}: Score = {metrics['overall_similarity_score']}")
```

---

## 📚 Statistical Significance

### When are differences "meaningful"?

**Rules of thumb**:

1. **Silhouette Score**: Difference > 0.1 is noticeable
2. **Davies-Bouldin**: Difference > 0.3 is significant
3. **Calinski-Harabasz**: Difference > 20% is meaningful
4. **Cluster sizes**: Wasserstein > 0.1 is noticeable
5. **Features**: Wasserstein > 0.2 per feature is significant

---

## 💡 Best Practices

### ✅ Do:
- Compare multiple metrics together
- Look at visualizations alongside numbers
- Test different parameter settings
- Document which metrics matter for your use case

### ❌ Don't:
- Rely on single metric alone
- Ignore visual inspection
- Expect perfect scores (80%+ is excellent!)
- Compare metrics across very different datasets

---

## 🎓 Example Interpretation

```json
{
  "overall_similarity_score": {
    "score": 87.3,
    "grade": "A-"
  },
  "silhouette_score": {
    "real": 0.524,
    "simulated": 0.518,
    "difference": 0.006
  },
  "davies_bouldin_index": {
    "real": 0.89,
    "simulated": 0.93,
    "difference": 0.04
  },
  "cluster_center_distance": {
    "mean_distance": 0.23
  }
}
```

**Interpretation**:
- ✅ Overall score 87.3% = Grade A- (Very Good)
- ✅ Silhouette difference 0.006 = Nearly identical cluster quality
- ✅ Davies-Bouldin difference 0.04 = Very similar separation
- ✅ Center distance 0.23 = Clusters in similar locations

**Conclusion**: Excellent simulation quality. Safe to use for research, data sharing, or ML training.

---

## 📖 References

1. Silhouette Score: Rousseeuw, P.J. (1987). Journal of Computational and Applied Mathematics.
2. Davies-Bouldin Index: Davies, D.L. & Bouldin, D.W. (1979). IEEE Transactions on Pattern Analysis.
3. Calinski-Harabasz: Caliński, T. & Harabasz, J. (1974). Communications in Statistics.
4. Wasserstein Distance: Vaserstein, L.N. (1969). Problems of Information Transmission.

---

**Last Updated**: 2024
**Version**: 1.0.0
