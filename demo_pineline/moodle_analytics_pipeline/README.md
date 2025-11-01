# Moodle Analytics Pipeline - GMM-Based

## 🎯 Overview

**Moodle Analytics Pipeline** là hệ thống phân tích và sinh dữ liệu học sinh **dựa trên Gaussian Mixture Model (GMM)** - thay thế hoàn toàn phương pháp rule-based simulation trước đây.

### ✨ Điểm mới so với phiên bản cũ

- ✅ **Feature Selection tự động**: Loại bỏ features không cần thiết dựa trên variance và correlation
- ✅ **Optimal Clustering với GMM**: Tự động tìm số cụm tối ưu (BIC, AIC, Silhouette)
- ✅ **GMM-based Data Generation**: Sinh dữ liệu synthetic từ GMM (không còn rule-based)
- ✅ **Comprehensive Validation**: Statistical tests (KS test, Chi-square) và comparison
- ✅ **Tự động hóa hoàn toàn**: Không cần can thiệp thủ công
- ✅ **Khoa học và minh bạch**: Mọi quyết định đều có metrics và visualizations

---

## 🔄 Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   MOODLE ANALYTICS PIPELINE                      │
│                        (GMM-BASED)                               │
└─────────────────────────────────────────────────────────────────┘

📊 PHASE 1: Feature Extraction
   ├─ Load grades & logs data
   ├─ Extract features (events, actions, grades, etc.)
   └─ Normalize features (MinMax/Z-score)
   
🔍 PHASE 2: Feature Selection
   ├─ Calculate variance scores
   ├─ Filter low-variance features
   ├─ Detect high-correlation features
   ├─ Rank and select optimal features
   └─ Output: Selected features list
   
🎯 PHASE 3: Optimal Clustering (GMM)
   ├─ Test k from 2 to 10
   ├─ Calculate BIC, AIC, Silhouette for each k
   ├─ Select optimal k (composite score)
   ├─ Fit GMM with optimal k
   └─ Output: Optimal k, GMM model, clusters
   
🔮 PHASE 4: GMM Data Generation
   ├─ Load real data with selected features
   ├─ Sample synthetic data from GMM
   ├─ Assign cluster labels and quality groups
   ├─ Visualize real vs synthetic (PCA, distributions)
   └─ Output: Synthetic students dataset
   
✅ PHASE 5: Validation
   ├─ Statistical tests (KS test for each feature)
   ├─ Distribution comparison (mean, std, skewness)
   ├─ Correlation matrix similarity
   ├─ Cluster distribution comparison (Chi-square)
   ├─ Calculate overall quality score
   └─ Output: Validation report + visualizations
   
📈 PHASE 6: Additional Comparison
   └─ Generate additional comparison plots
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd demo_pineline/moodle_analytics_pipeline

# Install dependencies
pip install -r requirements.txt
```

### Run Pipeline

```bash
python main.py
```

Hoặc tùy chỉnh parameters:

```python
from core import MoodleAnalyticsPipeline

pipeline = MoodleAnalyticsPipeline(base_output_dir='outputs')

results = pipeline.run_full_pipeline(
    grades_path='../data/udk_moodle_grades_course_670.filtered.csv',
    logs_path='../data/udk_moodle_log_course_670.filtered.csv',
    n_synthetic_students=200,         # Số học sinh synthetic
    variance_threshold=0.01,          # Threshold lọc variance
    correlation_threshold=0.95,       # Threshold lọc correlation
    max_features=15,                  # Max số features chọn
    k_range=range(2, 11)             # Range k để test
)
```

---

## 📊 Output Structure

```
outputs/
├── features/                          # PHASE 1
│   ├── features_raw.csv
│   ├── features_scaled.json
│   └── feature_statistics.json
│
├── feature_selection/                 # PHASE 2
│   ├── feature_selection_analysis.png
│   ├── feature_selection_report.json
│   └── feature_selection_report.txt
│
├── optimal_clusters/                  # PHASE 3
│   ├── optimal_clusters_evaluation.png
│   ├── optimal_clusters_report.json
│   └── optimal_clusters_report.txt
│
├── gmm_generation/                    # PHASE 4
│   ├── synthetic_students_gmm.csv
│   ├── synthetic_students_gmm.json
│   ├── gmm_generation_summary.json
│   ├── real_vs_synthetic_pca.png
│   ├── feature_distributions_comparison.png
│   └── correlation_comparison.png
│
├── validation/                        # PHASE 5
│   ├── validation_report.json
│   ├── validation_report.txt
│   ├── ks_test_results.png
│   └── distribution_boxplots.png
│
└── comparison/                        # PHASE 6
    └── (additional comparison plots)
```

---

## 🧪 Core Modules

### 1. FeatureExtractor
Trích xuất features từ Moodle logs và grades.

### 2. FeatureSelector ⭐ NEW
- Tính variance và correlation scores
- Loại bỏ low-variance features
- Loại bỏ highly-correlated features (redundant)
- Rank features theo importance

### 3. OptimalClusterFinder ⭐ NEW
- Test multiple k values (2-10)
- Calculate BIC, AIC, Silhouette
- Automated optimal k selection
- Comprehensive evaluation plots

### 4. GMMDataGenerator ⭐ NEW
- Fit GMM on real data
- Sample synthetic data from GMM distribution
- Assign cluster labels và quality groups
- Validate distribution similarity

### 5. ValidationMetrics ⭐ NEW
- Kolmogorov-Smirnov tests
- Distribution comparisons
- Correlation matrix similarity
- Overall quality scoring

---

## 📈 Key Metrics

### Feature Selection Metrics
- **Variance score**: Độ biến thiên của feature
- **Correlation score**: Độ tương quan giữa features
- **Composite score**: Tổng hợp variance + stability

### Clustering Metrics
- **BIC (Bayesian Information Criterion)**: Lower is better
- **AIC (Akaike Information Criterion)**: Lower is better
- **Silhouette Score**: 0-1, higher is better (>0.5: good)
- **Composite Score**: Weighted combination (0-1)

### Validation Metrics
- **KS Test p-value**: >0.05 → distributions are similar
- **Chi-square p-value**: >0.05 → cluster distributions are similar
- **Correlation Similarity**: 0-1, higher is better
- **Overall Quality Score**: 0-100% (Excellent: >85%, Good: >70%)

---

## 🎓 Scientific Approach

### 1. Feature Selection
- **Variance threshold**: Loại bỏ features có variance < 0.01 (ít thông tin)
- **Correlation threshold**: Loại bỏ features có correlation > 0.95 (redundant)
- **Ranking**: Composite score = 0.7 × variance + 0.3 × stability

### 2. Optimal Clustering
- **Strategy**: Test k từ 2-10, tính BIC/AIC/Silhouette cho mỗi k
- **Selection**: Chọn k có composite score cao nhất (0.5×BIC + 0.5×Silhouette)
- **Validation**: Kiểm tra convergence và iteration count

### 3. GMM Data Generation
- **Model**: Gaussian Mixture Model với covariance_type='full'
- **Sampling**: Sample từ GMM distribution (không dùng mean+noise như cũ)
- **Labeling**: Tự động map clusters sang quality labels (giỏi/khá/yếu)

### 4. Validation
- **Statistical tests**: KS test (mỗi feature), Chi-square test (cluster distribution)
- **Quality score**: 0.4×KS_pass_rate + 0.3×corr_similarity + 0.3×(1-mean_error)

---

## 🔧 Configuration

Edit `config.py` để tùy chỉnh:

```python
# Feature Selection
VARIANCE_THRESHOLD = 0.01
CORRELATION_THRESHOLD = 0.95
MAX_SELECTED_FEATURES = 15

# GMM Clustering
MIN_CLUSTERS = 2
MAX_CLUSTERS = 10
GMM_COVARIANCE_TYPE = 'full'

# Generation
N_SYNTHETIC_STUDENTS = 200

# Validation
KS_TEST_ALPHA = 0.05
MIN_QUALITY_SCORE_EXCELLENT = 85
MIN_QUALITY_SCORE_GOOD = 70
```

---

## 📝 Example Usage

### Basic Usage
```python
from core import MoodleAnalyticsPipeline

pipeline = MoodleAnalyticsPipeline()
results = pipeline.run_full_pipeline(
    grades_path='data/grades.csv',
    logs_path='data/logs.csv'
)

print(f"Optimal k: {results['optimal_k']}")
print(f"Quality Score: {results['validation_results']['overall_quality_score']['score']:.1f}%")
```

### Advanced Usage - Custom Modules
```python
from core import (
    FeatureExtractor,
    FeatureSelector,
    OptimalClusterFinder,
    GMMDataGenerator,
    ValidationMetrics
)

# 1. Extract features
extractor = FeatureExtractor()
features = extractor.process_pipeline(grades_path, logs_path, output_dir)

# 2. Select features
selector = FeatureSelector(variance_threshold=0.01, correlation_threshold=0.95)
selected = selector.process_pipeline(features, output_dir)

# 3. Find optimal k
finder = OptimalClusterFinder(k_range=range(2, 11))
optimal_k, gmm = finder.process_pipeline(features[selected].values, output_dir)

# 4. Generate synthetic data
generator = GMMDataGenerator(optimal_gmm=gmm)
synthetic = generator.process_pipeline(
    features_path, selected, optimal_k, n_synthetic=200, output_dir
)

# 5. Validate
validator = ValidationMetrics()
results = validator.process_pipeline(real_path, synthetic_path, selected, output_dir)

print(f"Quality: {results['overall_quality_score']['grade']}")
```

---

## 📚 References

- **GMM**: Gaussian Mixture Models for clustering
- **BIC/AIC**: Model selection criteria
- **Silhouette Score**: Cluster quality metric
- **KS Test**: Distribution similarity test

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License

---

## 🔗 Related Files

- `QUICKSTART.md`: Quick start guide with examples
- `MODULE_SUMMARY.md`: Detailed module documentation
- `METRICS_GUIDE.md`: Metrics explanation
- `config.py`: Configuration parameters

---

**Last Updated**: November 2025  
**Version**: 3.0 (GMM-based)
