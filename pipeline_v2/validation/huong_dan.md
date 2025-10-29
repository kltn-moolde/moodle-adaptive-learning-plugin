### Hướng Dẫn Code Validate Synthetic Data: So Sánh Phân Phối Với Dataset Gốc

Dựa trên phân tích validation tôi mô tả trước (univariate, multivariate, clusters), dưới đây là **code Python Jupyter Notebook (.ipynb) đầy đủ** để chạy. Code load gốc và synthetic (từ simulate trước: synth_logs_df, synth_grades_df, synth_df), tính metrics (KS/chi-square/Pearson/silhouette), visual (plots so sánh), và report table. Chạy trong Jupyter (Shift+Enter từng cell). Giả sử file CSV synthetic đã save từ simulate.

**Yêu cầu**: `pip install scikit-learn scipy pandas numpy matplotlib seaborn statsmodels` (nếu chưa). Nếu n nhỏ, tests robust.

#### Jupyter Notebook Code (Cells)

**Cell 1: Markdown - Giới thiệu**
```
# Validate Synthetic Data Moodle: So Sánh Phân Phối Với Gốc

- Load gốc & synthetic.
- Univariate: KS/chi-square cho categorical/count/continuous.
- Multivariate: Pearson corr.
- Clusters: Silhouette/ARI.
- Report: Table metrics, threshold pass (p>0.05, Δ<0.1).
- Iterate nếu fail: Adjust bias/GMM.
```

**Cell 2: Code - Import Và Load Data**
```python
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats.contingency import chi2_contingency
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.contingency_tables import mcnemar  # Cho chi-square nếu cần

# Load gốc
log_orig = pd.read_csv('udk_moodle_log_course_670.csv', parse_dates=['timecreated'])
grades_orig = pd.read_csv('udk_moodle_grades_course_670.csv')

# Load synthetic (từ simulate)
synth_logs = pd.read_csv('synthetic_logs.csv', parse_dates=['timecreated'])
synth_grades = pd.read_csv('synthetic_grades.csv')
synth_features = pd.read_csv('synthetic_features.csv')  # Nếu save synth_df từ GMM, columns: actions, finalgrade, group

# Preprocess chung (filter null, clip outliers)
log_orig = log_orig.dropna(subset=['action', 'timecreated'])
grades_orig = grades_orig.dropna(subset=['finalgrade'])
synth_logs = synth_logs.dropna(subset=['action', 'timecreated'])
synth_grades = synth_grades.dropna(subset=['finalgrade'])

# Tính features gốc nếu chưa (actions/user)
user_actions_orig = log_orig.groupby('userid').size().to_frame('actions')
avg_grades_orig = grades_orig.groupby('userid')['finalgrade'].mean().to_frame('finalgrade')
features_orig = pd.merge(user_actions_orig, avg_grades_orig, left_index=True, right_index=True, how='inner')

print("Shapes - Orig: Logs", log_orig.shape, "Grades", grades_orig.shape, "Features", features_orig.shape)
print("Shapes - Synth: Logs", synth_logs.shape, "Grades", synth_grades.shape, "Features", synth_features.shape)
```

**Cell 3: Markdown - Step 2: Univariate Validation**
```
## Univariate: So Phân Phối Riêng Lẻ

- Events/Actions: Chi-square probs.
- Hourly: KS-test.
- Actions/User: KS vs NB, var ratio.
- Finalgrade: KS-test, skewness.
```

**Cell 4: Code - Univariate Tests**
```python
# 1. Events/Actions (Categorical - Chi-square)
def chi2_probs(probs_orig, probs_synth):
    common_keys = set(probs_orig.keys()) & set(probs_synth.keys())
    cont_table = np.array([[probs_orig.get(k, 0) for k in common_keys],
                           [probs_synth.get(k, 0) for k in common_keys]])
    chi2, p_chi, dof, expected = chi2_contingency(cont_table)
    return chi2, p_chi

# Probs events/actions
probs_event_orig = log_orig['eventname'].value_counts(normalize=True)
probs_event_synth = synth_logs['eventname'].value_counts(normalize=True)
chi_event, p_event = chi2_probs(probs_event_orig, probs_event_synth)

probs_action_orig = log_orig['action'].value_counts(normalize=True)
probs_action_synth = synth_logs['action'].value_counts(normalize=True)
chi_action, p_action = chi2_probs(probs_action_orig, probs_action_synth)

print(f"Events Chi-square p: {p_event:.4f} (>0.05: giống)")
print(f"Actions Chi-square p: {p_action:.4f} (>0.05: giống)")

# 2. Hourly Time (KS-test)
log_orig['hour'] = log_orig['timecreated'].dt.hour
synth_logs['hour'] = synth_logs['timecreated'].dt.hour
hour_orig = log_orig['hour'].value_counts(normalize=True).sort_index().values
hour_synth = synth_logs['hour'].value_counts(normalize=True).sort_index().reindex(hour_orig.index, fill_value=0).values
ks_hour_stat, ks_hour_p = stats.ks_2samp(hour_orig, hour_synth)
print(f"Hourly KS p: {ks_hour_p:.4f} (>0.05: giống)")

# 3. Actions/User (Var ratio & KS vs empirical CDF)
actions_orig = features_orig['actions'].values
actions_synth = synth_features['actions'].values
var_ratio_orig = actions_orig.var() / actions_orig.mean()
var_ratio_synth = actions_synth.var() / actions_synth.mean()
print(f"Actions Var/Mean Ratio - Orig: {var_ratio_orig:.0f}, Synth: {var_ratio_synth:.0f} (Δ<20%: OK)")

# KS empirical (sắp xếp cho CDF)
ks_actions_stat, ks_actions_p = stats.ks_2samp(actions_orig, actions_synth)
print(f"Actions KS p: {ks_actions_p:.4f} (>0.05: giống)")

# 4. Finalgrade (KS-test & skewness)
grades_orig_vals = grades_orig['finalgrade'].values
grades_synth_vals = synth_grades['finalgrade'].values
ks_grade_stat, ks_grade_p = stats.ks_2samp(grades_orig_vals, grades_synth_vals)
skew_orig = stats.skew(grades_orig_vals)
skew_synth = stats.skew(grades_synth_vals)
print(f"Grades KS p: {ks_grade_p:.4f} (>0.05: giống)")
print(f"Skewness - Orig: {skew_orig:.3f}, Synth: {skew_synth:.3f} (Δ<0.2: OK)")

# Visual univariate
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
# Actions hist
axes[0,0].hist(actions_orig, bins=20, alpha=0.7, label='Orig')
axes[0,0].hist(actions_synth, bins=20, alpha=0.7, label='Synth')
axes[0,0].legend()
axes[0,0].set_title('Actions/User')

# Grades hist
axes[0,1].hist(grades_orig_vals, bins=20, alpha=0.7, label='Orig')
axes[0,1].hist(grades_synth_vals, bins=20, alpha=0.7, label='Synth')
axes[0,1].legend()
axes[0,1].set_title('Finalgrade')

# Hourly probs
pd.Series(hour_orig).plot(ax=axes[1,0], label='Orig')
pd.Series(hour_synth).plot(ax=axes[1,0], label='Synth')
axes[1,0].legend()
axes[1,0].set_title('Hourly Probs')

# Action probs bar (top 5)
top_actions_orig = probs_action_orig.head()
top_actions_synth = probs_action_synth.reindex(top_actions_orig.index, fill_value=0).head()
x = np.arange(len(top_actions_orig))
width = 0.35
axes[1,1].bar(x - width/2, top_actions_orig.values, width, label='Orig')
axes[1,1].bar(x + width/2, top_actions_synth.values, width, label='Synth')
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels(top_actions_orig.index)
axes[1,1].legend()
axes[1,1].set_title('Top Action Probs')
plt.tight_layout()
plt.show()
```

**Cell 5: Markdown - Step 3: Multivariate Validation**
```
## Multivariate: So Corr Và Relations

- Pearson corr actions-grade.
- Conditional mean per group (t-test giống).
```

**Cell 6: Code - Multivariate Tests**
```python
# Pearson corr (joint)
corr_orig = features_orig['actions'].corr(features_orig['finalgrade'])
corr_synth = synth_features['actions'].corr(synth_features['finalgrade'])
print(f"Corr - Orig: {corr_orig:.3f}, Synth: {corr_synth:.3f}, Δ: {abs(corr_orig - corr_synth):.3f} (<0.1: OK)")

# Visual corr
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.scatterplot(data=features_orig, x='actions', y='finalgrade', ax=axes[0])
axes[0].set_title('Orig Corr')
sns.scatterplot(data=synth_features, x='actions', y='finalgrade', hue='group', ax=axes[1])
axes[1].set_title('Synth Corr (by Group)')
plt.show()

# Conditional: Mean grade per group (gốc cần assign groups tương tự GMM)
# Assign groups gốc (dùng GMM labels từ simulate Step 2)
features_orig['group'] = 'khá'  # Placeholder; dùng GMM.predict nếu có labels_orig
group_means_orig = features_orig.groupby('group')['finalgrade'].mean()
group_means_synth = synth_features.groupby('group')['finalgrade'].mean()
print("Mean Grade per Group:\n", pd.DataFrame({'Orig': group_means_orig, 'Synth': group_means_synth}))

# T-test per group (ví dụ giỏi)
from scipy.stats import ttest_ind
if 'giỏi' in features_orig['group'].values and 'giỏi' in synth_features['group'].values:
    t_stat, t_p = ttest_ind(features_orig[features_orig['group']=='giỏi']['finalgrade'], 
                            synth_features[synth_features['group']=='giỏi']['finalgrade'])
    print(f"Grade Giỏi T-test p: {t_p:.4f} (>0.05: giống)")
```

**Cell 7: Markdown - Step 4: Clusters Validation**
```
## Clusters: Silhouette & ARI

- Silhouette trên K-means=3.
- ARI so GMM vs K-means.
```

**Cell 8: Code - Clusters Tests**
```python
# Scale synthetic features cho K-means
scaler_synth = StandardScaler()
X_synth_scaled = scaler_synth.fit_transform(synth_features[['actions', 'finalgrade']])

# K-means=3 trên synthetic
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_synth_scaled)
sil_kmeans = silhouette_score(X_synth_scaled, kmeans_labels)
ari = adjusted_rand_score(synth_features['cluster'], kmeans_labels)  # So với GMM labels
print(f"Synthetic Silhouette (K-means): {sil_kmeans:.3f} (>0.4: rõ)")
print(f"ARI (GMM vs K-means): {ari:.3f} (>0.7: stable)")

# Plot silhouette nếu cần (sklearn có function, nhưng đơn giản)
sns.scatterplot(data=synth_features, x='actions', y='finalgrade', hue=kmeans_labels)
plt.title('K-means Clusters Synthetic')
plt.show()

# ANOVA per cluster (khác biệt groups)
from scipy.stats import f_oneway
groups = [synth_features[synth_features['group']==g]['actions'].values for g in cluster_names.values()]
anova_stat, anova_p = f_oneway(*groups)
print(f"ANOVA Actions per Group p: {anova_p:.4f} (<0.05: khác biệt rõ)")
```

**Cell 9: Markdown - Step 5: Report Tổng Hợp**
```
## Report Tổng Hợp

- Table metrics với pass/fail.
- Nếu >80% pass, OK; else iterate.
```

**Cell 10: Code - Report Table**
```python
# Tạo report table
report_data = {
    'Metric': ['Events Chi p', 'Actions Chi p', 'Hourly KS p', 'Actions KS p', 'Grades KS p', 'Skew Δ', 'Corr Δ', 'Sil Synth', 'ARI'],
    'Value': [p_event, p_action, ks_hour_p, ks_actions_p, ks_grade_p, abs(skew_orig - skew_synth), abs(corr_orig - corr_synth), sil_kmeans, ari],
    'Threshold': ['>0.05', '>0.05', '>0.05', '>0.05', '>0.05', '<0.2', '<0.1', '>0.4', '>0.7'],
    'Pass': ['Yes' if p_event > 0.05 else 'No', 'Yes' if p_action > 0.05 else 'No',
             'Yes' if ks_hour_p > 0.05 else 'No', 'Yes' if ks_actions_p > 0.05 else 'No',
             'Yes' if ks_grade_p > 0.05 else 'No', 'Yes' if abs(skew_orig - skew_synth) < 0.2 else 'No',
             'Yes' if abs(corr_orig - corr_synth) < 0.1 else 'No', 'Yes' if sil_kmeans > 0.4 else 'No', 'Yes' if ari > 0.7 else 'No']
}

report_df = pd.DataFrame(report_data)
print(report_df)
pass_rate = (report_df['Pass'] == 'Yes').mean() * 100
print(f"\nOverall Pass Rate: {pass_rate:.1f}% (>80%: Proceed)")
```

**Cell 11: Markdown - Kết Luận**
```
## Kết Luận & Iterate

- Nếu pass rate >80%, synthetic OK cho ứng dụng (e.g., train model).
- Fail cụ thể: E.g., nếu Actions KS p<0.05, tăng dispersion NB; nếu Corr Δ>0.1, re-fit GMM.
- Tiếp theo: Train model (e.g., logistic predict yếu) trên synthetic, test trên gốc.
```

#### Hướng Dẫn Chạy
- **Jupyter**: Paste cells, run all. Nếu error (e.g., no 'cluster' column), add từ simulate.
- **Adjust**: Thresholds dựa paper (error <10% ~ p>0.05). Visual giúp spot lệch (e.g., hist mismatch).
- **Output ví dụ**: Report table với Yes/No, pass rate 90% → OK.

Nếu chạy và share report/output, tôi phân tích iterate nhé! 😊