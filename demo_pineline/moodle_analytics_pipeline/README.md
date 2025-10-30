# Moodle Analytics Pipeline

Complete end-to-end pipeline for Moodle learning analytics: Feature Extraction → Clustering → Data Simulation → Comparison Visualization

## 📋 Overview

This pipeline analyzes Moodle student data to:
1. **Extract features** from grades and log files
2. **Cluster students** into learning behavior groups
3. **Simulate synthetic student data** based on real patterns
4. **Compare** real vs simulated data with statistical tests

## 🗂️ Project Structure

```
moodle_analytics_pipeline/
├── main.py                         # Main pipeline orchestrator
├── core/
│   ├── __init__.py
│   ├── feature_extractor.py        # Feature extraction & normalization
│   ├── clustering_analyzer.py      # KMeans clustering & visualization
│   ├── data_simulator.py           # Synthetic data generation
│   └── comparison_visualizer.py    # Real vs Simulated comparison
└── outputs/                        # All pipeline outputs
    ├── features/                   # Extracted features
    ├── clustering/                 # Clustering results
    ├── simulation/                 # Simulated data
    └── comparison/                 # Comparison reports
```

## 🚀 Quick Start

### Installation

```bash
# Clone or download this module
cd moodle_analytics_pipeline

# Install dependencies
pip install pandas numpy scikit-learn matplotlib seaborn scipy
```

### Basic Usage

```python
from main import MoodleAnalyticsPipeline

# Initialize pipeline
pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs')

# Run complete pipeline
results = pipeline.run_full_pipeline(
    grades_path='path/to/grades.csv',
    logs_path='path/to/logs.csv',
    n_clusters=None,              # Auto-detect optimal K
    n_simulated_students=100,
    simulation_noise=0.1
)
```

### Command Line

```bash
# Run with default settings
python main.py

# Customize by editing main() function in main.py
```

## 📊 Pipeline Stages

### Stage 1: Feature Extraction

**Input:** Raw CSV files
- `udk_moodle_grades_course_670.filtered.csv`
- `udk_moodle_log_course_670.filtered.csv`

**Process:**
- Pivot event logs into feature matrix
- Extract interaction patterns (events, actions, targets)
- Normalize features to [0, 1] using MinMaxScaler

**Output:**
- `features_scaled.json` - Normalized feature matrix
- Feature statistics

### Stage 2: Clustering Analysis

**Input:** `features_scaled.json`

**Process:**
- Find optimal K using Elbow + Silhouette + Davies-Bouldin
- Perform KMeans clustering
- Generate cluster profiles and statistics

**Output:**
- `clustered_students.csv` - Students with cluster assignments
- `cluster_statistics.json` - Mean/std for each cluster
- `cluster_analysis.png` - Elbow & Silhouette plots
- `clusters_pca.png` - PCA visualization
- `cluster_profiles.png` - Radar charts

### Stage 3: Data Simulation

**Input:** `cluster_statistics.json`

**Process:**
- Sample cluster assignments from real distribution
- Generate features using Gaussian distribution
- Add configurable noise level

**Output:**
- `simulated_students.csv` - Synthetic student data
- `simulated_students.json` - JSON format
- `simulated_cluster_visualization.png` - PCA visualization of simulated clusters ⭐ NEW
- `simulation_summary.json` - Simulation statistics

### Stage 4: Comparison & Validation

**Input:**
- `clustered_students.csv` (real data)
- `simulated_students.csv` (simulated data)

**Process:**
- Compare feature distributions (KS test)
- Compare cluster proportions (Chi-square test)
- Calculate statistical summaries

**Output:**
- `comparison_dashboard.png` - 9-panel visualization
- `comparison_report.json` - Statistical test results
- `comparison_report.txt` - Human-readable report

### Stage 5: Cluster Comparison Analysis ⭐ NEW

**Input:**
- `clustered_students.csv` (real data with clusters)
- `simulated_students.csv` (simulated data)

**Process:**
- Re-cluster simulated data using KMeans
- Compare cluster quality metrics (Silhouette, Davies-Bouldin, Calinski-Harabasz)
- Calculate cluster center distances
- Compare cluster size distributions
- Compute overall similarity score (0-100%)

**Output:**
- `cluster_pca_comparison.png` - Side-by-side PCA visualizations
- `cluster_sizes_comparison.png` - Cluster size bar charts
- `cluster_profiles_comparison.png` - Radar chart comparisons
- `feature_distributions_comparison.png` - Feature histogram overlays
- `similarity_metrics_dashboard.png` - Comprehensive metrics dashboard
- `cluster_comparison_report.json` - Detailed similarity metrics
- `cluster_comparison_report.txt` - Human-readable analysis

**Key Metrics:**
- **Overall Similarity Score**: 0-100% with letter grade (A+ to D)
- **Silhouette Score**: Cluster cohesion and separation
- **Davies-Bouldin Index**: Cluster quality (lower = better)
- **Calinski-Harabasz Score**: Cluster definition (higher = better)
- **Cluster Center Distance**: Euclidean distance between centroids
- **Wasserstein Distance**: Distribution similarity
- **Feature Distribution Similarity**: Per-feature comparison

## 📈 Key Features

### Statistical Validation
- **Kolmogorov-Smirnov Test**: Compare feature distributions
- **Chi-Square Test**: Validate cluster proportions
- **Summary Statistics**: Mean, std, median comparison

### Visualizations
- Distribution histograms with overlays
- PCA scatter plots
- Radar charts for cluster profiles
- Comprehensive comparison dashboard

### Configurable Parameters
```python
pipeline.run_full_pipeline(
    grades_path='grades.csv',
    logs_path='logs.csv',
    n_clusters=5,                    # Fixed K or None for auto
    n_simulated_students=200,        # Simulation size
    simulation_noise=0.15            # Noise level (0-1)
)
```

## 🔧 Individual Module Usage

### Feature Extraction Only

```python
from core import FeatureExtractor

extractor = FeatureExtractor()
features = extractor.process_pipeline(
    grades_path='grades.csv',
    logs_path='logs.csv',
    output_dir='outputs/features'
)
```

### Clustering Only

```python
from core import ClusteringAnalyzer

analyzer = ClusteringAnalyzer()
clustered, stats = analyzer.process_pipeline(
    features_path='features_scaled.json',
    output_dir='outputs/clustering',
    n_clusters=5
)
```

### Simulation Only

```python
from core import DataSimulator

simulator = DataSimulator('cluster_statistics.json')
simulated = simulator.process_pipeline(
    n_students=100,
    output_dir='outputs/simulation',
    noise_level=0.1
)
```

### Comparison Only

```python
from core import ComparisonVisualizer

visualizer = ComparisonVisualizer()
visualizer.process_pipeline(
    real_path='real_students.csv',
    simulated_path='simulated_students.csv',
    features=['feature1', 'feature2'],
    output_dir='outputs/comparison'
)
```

### Cluster Comparison Only ⭐ NEW

```python
from core import ClusterComparison

comparison = ClusterComparison()
metrics = comparison.process_pipeline(
    real_path='clustered_students.csv',
    simulated_path='simulated_students.csv',
    n_clusters=5,
    output_dir='outputs/cluster_comparison'
)

# Access similarity score
print(f"Similarity: {metrics['overall_similarity_score']['score']:.2f}%")
print(f"Grade: {metrics['overall_similarity_score']['grade']}")
```

## 📝 Input Data Format

### Grades CSV
```csv
userid,course,grade
123,670,85.5
124,670,92.0
...
```

### Logs CSV
```csv
userid,eventname,action,target
123,course_viewed,view,course
123,quiz_started,start,quiz
...
```

## 📊 Output Examples

### Clustering Analysis
- **Elbow Plot**: Helps identify optimal K
- **Silhouette Score**: Cluster quality metric
- **PCA Visualization**: 2D projection of clusters
- **Radar Charts**: Multi-dimensional cluster profiles

### Comparison Dashboard (9 panels)
1-6. Feature distribution comparisons (real vs simulated)
7. Cluster proportion comparison
8-9. Statistical summaries

### Cluster Comparison ⭐ NEW
- **Side-by-side PCA**: Visual cluster comparison
- **Cluster Size Charts**: Distribution comparison
- **Profile Radar Charts**: Multi-dimensional comparison per cluster
- **Feature Distributions**: Histogram overlays
- **Metrics Dashboard**: Overall similarity gauge + detailed metrics
- **Similarity Score**: 0-100% with grade (A+ to D)

### Reports
```json
{
  "feature1": {
    "ks_statistic": 0.12,
    "ks_pvalue": 0.34,
    "distributions_similar": true
  },
  "clusters": {
    "chi2_statistic": 2.45,
    "chi2_pvalue": 0.78,
    "distributions_similar": true
  }
}
```

## 🧪 Testing

Each module includes test functions:

```bash
# Test feature extraction
python core/feature_extractor.py

# Test clustering
python core/clustering_analyzer.py

# Test simulation
python core/data_simulator.py

# Test comparison
python core/comparison_visualizer.py

# Test cluster comparison ⭐ NEW
python core/cluster_comparison.py

# Standalone cluster comparison demo
python demo_cluster_comparison.py
```

## 🔍 Troubleshooting

### Module not found
```bash
# Ensure you're in the correct directory
cd moodle_analytics_pipeline
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Input file not found
```bash
# Use absolute paths or verify relative paths
import os
print(os.path.abspath('data/grades.csv'))
```

### Memory errors with large datasets
```python
# Reduce feature count or sample data
features = features.sample(frac=0.5)  # Use 50% of data
```

## 📚 Dependencies

- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scikit-learn**: Machine learning (KMeans, PCA, MinMaxScaler)
- **matplotlib**: Visualization
- **seaborn**: Statistical plots
- **scipy**: Statistical tests

## 🎯 Use Cases

1. **Student Behavior Analysis**: Identify learning patterns
2. **Data Augmentation**: Generate synthetic training data
3. **Privacy-Preserving Research**: Share simulated instead of real data
4. **Model Validation**: Test ML models with realistic synthetic data
5. **What-If Analysis**: Simulate different student populations

## 📄 License

MIT License - Feel free to use and modify

## 👥 Contributing

Contributions welcome! Areas for improvement:
- Additional clustering algorithms (DBSCAN, Hierarchical)
- More sophisticated simulation (GANs, VAEs)
- Real-time pipeline execution
- Web dashboard interface

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainer.

---

**Version**: 1.0.0  
**Last Updated**: 2024
