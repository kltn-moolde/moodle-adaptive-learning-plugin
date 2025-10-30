# Quick Start Guide

Get started with Moodle Analytics Pipeline in 5 minutes!

## 📦 Installation (2 minutes)

### Step 1: Download/Clone
```bash
cd /path/to/your/projects
# Assuming you already have the moodle_analytics_pipeline folder
cd moodle_analytics_pipeline
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**That's it!** No complex setup required.

## 🚀 Run Your First Pipeline (3 minutes)

### Option A: Use Example Data

```bash
python example_usage.py
```

Select option **4** for quick start, or **1** for full demo.

### Option B: Use Your Own Data

Edit `main.py` and update the paths:

```python
results = pipeline.run_full_pipeline(
    grades_path='path/to/your/grades.csv',  # ← Change this
    logs_path='path/to/your/logs.csv',      # ← Change this
    n_clusters=None,  # Auto-detect optimal K
    n_simulated_students=100,
    simulation_noise=0.1
)
```

Then run:
```bash
python main.py
```

### Option C: Interactive Python

```python
from main import MoodleAnalyticsPipeline

# One-liner execution
pipeline = MoodleAnalyticsPipeline()
results = pipeline.run_full_pipeline(
    grades_path='data/grades.csv',
    logs_path='data/logs.csv'
)

# Results are in 'outputs/' directory
```

## 📊 Check Your Results

After running, check the `outputs/` directory:

```
outputs/
├── features/
│   └── features_scaled.json          # Extracted features
├── clustering/
│   ├── clustered_students.csv        # Students with clusters
│   ├── cluster_statistics.json       # Cluster profiles
│   ├── cluster_analysis.png          # Elbow & Silhouette plots
│   ├── clusters_pca.png              # PCA visualization
│   └── cluster_profiles.png          # Radar charts
├── simulation/
│   └── simulated_students.csv        # Synthetic data
└── comparison/
    ├── comparison_dashboard.png      # 9-panel comparison
    └── comparison_report.txt         # Statistical tests
```

## 🎯 What Each File Means

| File | What It Shows |
|------|---------------|
| `features_scaled.json` | Normalized features extracted from raw data |
| `clustered_students.csv` | Each student assigned to a learning behavior group |
| `cluster_statistics.json` | Average characteristics of each group |
| `cluster_analysis.png` | How we found the optimal number of groups |
| `clusters_pca.png` | Visual representation of student groups |
| `cluster_profiles.png` | What makes each group unique |
| `simulated_students.csv` | Synthetic students that look like real ones |
| `comparison_dashboard.png` | How similar are real vs simulated students? |
| `comparison_report.txt` | Statistical proof of similarity |

## 🔧 Common Customizations

### Change Number of Clusters

```python
pipeline.run_full_pipeline(
    ...,
    n_clusters=5  # Fixed to 5 clusters instead of auto-detect
)
```

### Generate More Synthetic Students

```python
pipeline.run_full_pipeline(
    ...,
    n_simulated_students=500  # Generate 500 students
)
```

### Adjust Simulation Realism

```python
pipeline.run_full_pipeline(
    ...,
    simulation_noise=0.05  # More realistic (less noise)
    # or
    simulation_noise=0.2   # More variety (more noise)
)
```

## ❓ Troubleshooting

### "Module not found"
```bash
cd moodle_analytics_pipeline  # Make sure you're in the right directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "File not found"
Use absolute paths:
```python
grades_path='/full/path/to/grades.csv'
```

### "Out of memory"
Reduce dataset size:
```python
import pandas as pd
df = pd.read_csv('large_file.csv')
df.sample(frac=0.5).to_csv('smaller_file.csv')  # Use 50%
```

## 📖 Next Steps

- **Understand the pipeline**: Read `README.md` for detailed documentation
- **Explore examples**: Run `example_usage.py` and select different options
- **Customize settings**: Edit `config.py` to adjust parameters
- **Use individual modules**: See README for standalone module usage

## 💡 Tips for First-Time Users

1. **Start with auto-detect K**: Let the pipeline find optimal clusters
2. **Check the visualizations**: They're more intuitive than raw numbers
3. **Read the comparison report**: It tells you if simulation is good
4. **Experiment with noise**: Try 0.05, 0.1, 0.15 to see differences
5. **Don't worry about errors**: Logs are saved to `pipeline.log`

## 🎓 What's Happening Behind the Scenes?

```
Your CSV files
      ↓
[Feature Extraction] → Creates a matrix of student behaviors
      ↓
[Clustering] → Groups students by similar patterns
      ↓
[Simulation] → Generates fake students that mimic real ones
      ↓
[Comparison] → Proves the fake data is realistic
      ↓
Pretty charts and statistics! 📊
```

## 🆘 Need Help?

- Check `README.md` for detailed docs
- Look at `example_usage.py` for code samples
- Review `pipeline.log` for error messages
- Open an issue on GitHub

---

**Time to get started**: ~5 minutes  
**Skill level**: Beginner-friendly  
**Prerequisites**: Python 3.7+ and pip

Happy analyzing! 🚀
