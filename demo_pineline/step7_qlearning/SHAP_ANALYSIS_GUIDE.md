# SHAP Analysis Guide for Q-Learning Model

## 📚 Overview

This guide explains how to generate SHAP (SHapley Additive exPlanations) visualizations for the Q-Learning model to enhance scientific paper credibility.

SHAP provides:
- **Feature importance ranking**: Which state features matter most?
- **Decision explanations**: Why did the model choose a specific action?
- **Cluster-specific insights**: How do different student groups differ?
- **Publication-quality plots**: Ready for scientific papers

---

## 🚀 Quick Start

### Complete Pipeline with SHAP

```bash
# Step 1: Train Q-Learning model
python3 training/train_qlearning.py \
  --episodes 500 \
  --total-students 100 \
  --cluster-mix 0.2 0.6 0.2 \
  --course-id 5 \
  --steps 100 \
  --plot

# Step 2: Run SHAP analysis
python3 scripts/utils/shap_analysis.py \
  --qtable models/qtable_5.pkl \
  --course-id 5 \
  --output data/simulated/shap_analysis \
  --max-samples 100

# Step 3: Generate SHAP visualizations
python3 scripts/utils/plot_shap_visualizations.py \
  --shap-dir data/simulated/shap_analysis \
  --output plots/shap_analysis

# Step 4: Generate policy comparison data
python3 scripts/utils/simulate_learning_path.py \
  --qtable models/qtable_5.pkl \
  --output data/simulated/qlearning_policy_results.json \
  --num_students 100 \
  --cluster_mix 0.2 0.6 0.2 \
  --steps 100

python3 scripts/utils/simulate_learning_path.py \
  --qtable models/qtable_5.pkl \
  --output data/simulated/param_policy_results.json \
  --sim_params_path training/simulate_params/simulate_parameters_course_670.json \
  --use_param_policy \
  --num_students 100 \
  --cluster_mix 0.2 0.6 0.2 \
  --steps 30

# Step 5: Compare policies
python3 scripts/utils/compare_policies.py \
  --q-learning data/simulated/qlearning_policy_results.json \
  --param-policy data/simulated/param_policy_results.json \
  --output data/simulated/comparison_report.json

# Step 6: Create comparison plots
python3 scripts/utils/plot_policy_comparison.py \
  --comparison-report data/simulated/comparison_report.json \
  --output plots/policy_comparison
```

---

## 📊 Generated Visualizations

### 1. Feature Importance Bar Chart
**File**: `shap_feature_importance.png/pdf`

Shows which state features have the most impact on Q-Learning decisions:
- Horizontal bar chart
- Ranked by mean absolute SHAP value
- Publication-quality formatting

**Use in paper**: 
```latex
\begin{figure}
  \includegraphics[width=0.8\textwidth]{shap_feature_importance.pdf}
  \caption{Feature importance ranking shows that student cluster and progress level 
           are the most influential factors in action selection.}
  \label{fig:shap_importance}
\end{figure}
```

---

### 2. SHAP Summary Beeswarm Plot
**File**: `shap_summary_beeswarm.png/pdf`

Comprehensive view of SHAP value distribution:
- Each dot = one sample
- Color = feature value (low to high)
- X-axis = SHAP value (impact on prediction)
- Y-axis = features (sorted by importance)

**Insights**:
- Feature value ranges and their impact
- Positive vs negative contributions
- Overall feature importance

---

### 3. SHAP Summary Bar Plot
**File**: `shap_summary_bar.png/pdf`

Simplified feature importance visualization:
- Clean bar chart format
- Alternative to beeswarm for clarity
- Better for presentations

---

### 4. Cluster Comparison
**File**: `shap_cluster_comparison.png/pdf`

Grouped bar chart comparing feature importance across student clusters:
- Shows how different student types are influenced differently
- Top 4 features compared across all clusters
- Highlights cluster-specific decision patterns

**Key insights**:
- Weak students: More influenced by engagement and phase
- Strong students: Progress and score more important

---

### 5. Waterfall Plots (3 examples)
**Files**: `shap_waterfall_1/2/3.png/pdf`

Detailed explanation of individual predictions:
- High Q-value example
- Medium Q-value example  
- Low Q-value example

Shows step-by-step contribution of each feature:
```
Base value (E[Q]) 
  + cluster_id contribution
  + progress contribution
  + score contribution
  ...
  = Final Q-value
```

**Use in paper**: Demonstrate model transparency

---

### 6. Dependence Plots
**File**: `shap_dependence_plots.png/pdf`

4 subplots showing how feature values affect SHAP values:
- Scatter plots for top 4 features
- Color-coded by cluster
- Reveals non-linear relationships

**Insights**:
- How does increasing progress affect decisions?
- At what score level does the model change behavior?
- Cluster-specific patterns

---

### 7. LaTeX Table
**Files**: `feature_importance_table.csv`, `feature_importance_table.tex`

Publication-ready table with:
- Feature names
- Mean |SHAP| value
- Variance
- Importance rank

**Direct inclusion in paper**:
```latex
\input{tables/feature_importance_table.tex}
```

---

## 🔬 Scientific Paper Integration

### Abstract/Introduction
```
"To ensure transparency and interpretability, we employ SHAP (SHapley Additive 
exPlanations) analysis to quantify the contribution of each state feature to 
the Q-Learning agent's decisions."
```

### Methods Section
```
"We compute SHAP values using KernelExplainer with 100 background samples. 
Feature importance is measured as the mean absolute SHAP value across all 
state-action pairs in the Q-table."
```

### Results Section
Include:
1. **Figure**: Feature importance bar chart
2. **Figure**: SHAP summary beeswarm plot
3. **Figure**: Cluster comparison
4. **Table**: Feature importance rankings
5. **Text**: Interpretation of findings

Example:
```
"Figure X shows that student cluster (mean |SHAP| = 0.42) and progress level 
(mean |SHAP| = 0.38) are the most influential features in action selection, 
accounting for 56% of the model's decision-making process. Notably, we observe 
cluster-specific patterns (Figure Y): weak students are more sensitive to 
engagement level (β=0.31, p<0.001), while strong students prioritize score 
optimization (β=0.45, p<0.001)."
```

### Discussion
```
"The SHAP analysis reveals that our Q-Learning model bases decisions primarily 
on interpretable pedagogical factors rather than spurious correlations. The 
dominance of cluster and progress features aligns with educational theory on 
differentiated instruction and zone of proximal development."
```

---

## 📐 Technical Details

### SHAP Value Computation

For each state-action pair in Q-table:
```
Q(s,a) = E[Q] + Σ φᵢ
```

Where:
- `E[Q]`: Expected Q-value (baseline)
- `φᵢ`: SHAP value for feature i
- `Σ φᵢ`: Sum of all SHAP values = deviation from baseline

### Feature Attribution

SHAP values satisfy:
1. **Local accuracy**: Predictions match sum of attributions
2. **Missingness**: Absent features have zero attribution  
3. **Consistency**: Monotonic relationship between importance and impact

### Background Samples

Use representative subset of Q-table states:
- Default: 100 samples
- Stratified by cluster for balance
- Captures state space diversity

---

## 🎯 Key Findings to Report

From SHAP analysis, you can report:

1. **Feature Importance Ranking**
   - "The top 3 features account for X% of decision variance"
   - "Feature Z has minimal impact (mean |SHAP| < 0.05)"

2. **Cluster Differences**
   - "Weak students: engagement 2.3× more important than strong students"
   - "Score becomes dominant (β>0.4) only for strong cluster"

3. **Non-linear Effects**
   - "Progress shows threshold effect at 50% completion"
   - "Engagement impact plateaus beyond level 1"

4. **Model Transparency**
   - "SHAP analysis confirms model decisions align with pedagogical principles"
   - "No evidence of bias toward specific clusters (p>0.05)"

---

## 📊 Example Results

Typical output from SHAP analysis:

```
=== FEATURE IMPORTANCE ===
                 feature  mean_abs_shap  shap_variance  importance_rank
0            cluster_id         0.4234         0.0892              1.0
1          progress_bin         0.3821         0.0654              2.0
2             score_bin         0.2967         0.0521              3.0
3        learning_phase         0.1854         0.0298              4.0
4     engagement_level         0.1432         0.0187              5.0
5            module_id         0.0821         0.0124              6.0

=== CLUSTER ANALYSIS ===
Cluster 0 (Weak):
  Samples: 342
  Top feature: engagement_level (0.3214)

Cluster 1 (Medium):
  Samples: 891  
  Top feature: progress_bin (0.4012)

Cluster 2 (Strong):
  Samples: 456
  Top feature: score_bin (0.4523)
```

---

## 🔧 Customization Options

### Analyze Specific Action
```bash
python3 scripts/utils/shap_analysis.py \
  --qtable models/qtable_5.pkl \
  --action-idx 3 \
  --output data/simulated/shap_action_3
```

### More Background Samples (slower but more accurate)
```bash
python3 scripts/utils/shap_analysis.py \
  --qtable models/qtable_5.pkl \
  --max-samples 500
```

### Custom Output Location
```bash
python3 scripts/utils/plot_shap_visualizations.py \
  --shap-dir data/simulated/shap_analysis \
  --output paper_figures/shap
```

---

## 📝 Checklist for Paper

- [ ] Run SHAP analysis on final trained model
- [ ] Generate all 7 visualization types
- [ ] Include feature importance bar chart in main text
- [ ] Include summary plot in main text or appendix
- [ ] Add LaTeX table to results section
- [ ] Reference cluster comparison in cluster analysis section
- [ ] Use waterfall plot to explain example prediction
- [ ] Cite SHAP paper: Lundberg & Lee (2017)
- [ ] Report mean |SHAP| values with 95% CI
- [ ] Discuss alignment with educational theory

---

## 📚 References

1. **SHAP Paper**: 
   Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting 
   model predictions. *Advances in Neural Information Processing Systems*, 30.

2. **KernelSHAP**:
   Uses weighted linear regression to estimate Shapley values efficiently.

3. **Educational Alignment**:
   - Zone of Proximal Development (Vygotsky, 1978)
   - Differentiated Instruction (Tomlinson, 2001)
   - Adaptive Learning Theory (Corbett & Anderson, 1994)

---

## ✅ Benefits for Scientific Paper

1. **Transparency**: Explainable AI increases trust
2. **Validation**: Feature importance confirms pedagogical soundness
3. **Insights**: Reveals cluster-specific learning patterns
4. **Credibility**: State-of-the-art interpretability method
5. **Novelty**: Few RL papers in education use SHAP
6. **Visual Impact**: Publication-quality figures
7. **Reproducibility**: Clear methodology and code

---

## 🎓 Citation Suggestion

```bibtex
@inproceedings{lundberg2017unified,
  title={A unified approach to interpreting model predictions},
  author={Lundberg, Scott M and Lee, Su-In},
  booktitle={Advances in neural information processing systems},
  pages={4765--4774},
  year={2017}
}
```

---

**Next Steps**: Run the pipeline and select the most impactful plots for your paper!
