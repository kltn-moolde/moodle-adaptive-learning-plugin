### Hướng Dẫn Step-by-Step Simulate Synthetic Data Từ Dataset Moodle

Dựa trên chiến lược hybrid tôi phân tích trước (GMM cho impose 3 cụm trên features [actions/user, finalgrade] để giữ corr 0.75, rule-based bias theo cụm cho logs, NB cho over-dispersion actions, Beta cho skewed grades), dưới đây là hướng dẫn chi tiết để simulate. Quy trình dùng **Python (scikit-learn, scipy, pandas)**, dễ chạy trong Jupyter Notebook. Giả sử bạn có hai file CSV (logs và grades) ở thư mục hiện tại.

**Mục tiêu**: Tạo synthetic dataset x10 lớn (140k logs, 2.3k grades), giữ phân phối gốc (probs events ~80% viewed, hourly peak 11-13h, var actions cao, mean grade 7.64), nhưng với 3 cụm rõ (giỏi: high actions/grade; khá: medium; yếu: low) – silhouette >0.4.

**Yêu cầu môi trường**: `pip install scikit-learn scipy pandas numpy matplotlib seaborn` (nếu chưa có). Chạy từng step trong notebook để debug.

#### Step 1: Chuẩn Bị Data Và Tính Features (Load & Merge)
- **Mô tả**: Load hai file, tính actions/user từ logs, merge với finalgrade theo userid. Scale features cho GMM (vì var actions >> grade). Đây là base để fit GMM.
- **Lý do**: Merge capture corr (0.75), scale tránh bias over-dispersion.
- **Code** (Chạy cell này đầu tiên):
  ```python
  import pandas as pd
  import numpy as np
  from sklearn.preprocessing import StandardScaler
  from sklearn.mixture import GaussianMixture
  from sklearn.metrics import silhouette_score
  from scipy import stats
  import matplotlib.pyplot as plt
  import seaborn as sns

  # Load files
  log_df = pd.read_csv('udk_moodle_log_course_670.csv', parse_dates=['timecreated'])
  grades_df = pd.read_csv('udk_moodle_grades_course_670.csv')

  # Tính features từ logs
  user_actions = log_df.groupby('userid').size().to_frame('actions')

  # Merge với grades (avg finalgrade nếu multi per user)
  avg_grades = grades_df.groupby('userid')['finalgrade'].mean().to_frame('finalgrade')
  features_df = pd.merge(user_actions, avg_grades, left_index=True, right_index=True, how='inner')
  features_df = features_df.fillna({'finalgrade': features_df['finalgrade'].mean()})  # Fill nếu null

  # Scale features
  scaler = StandardScaler()
  X_scaled = scaler.fit_transform(features_df[['actions', 'finalgrade']])

  print("Features shape:", features_df.shape)
  print(features_df.head())
  print("Corr check:", features_df['actions'].corr(features_df['finalgrade']))
  ```
- **Output mong đợi**: DataFrame ~233 rows (users overlap), corr ~0.75.
- **Kiểm tra**: Nếu merge <100 users, adjust how='outer' và fill 0.

#### Step 2: Fit GMM Để Impose 3 Cụm (Joint Distribution)
- **Mô tả**: Fit GMM trên X_scaled để học joint dist (capture corr), với 3 components (impose giỏi/khá/yếu). EM sẽ tự assign means (e.g., giỏi: actions cao, grade ~9).
- **Lý do**: Corr mạnh → GMM giữ relation; n_components=3 làm rõ cụm dù gốc over-dispersed.
- **Code** (Tiếp theo Step 1):
  ```python
  # Fit GMM
  gmm = GaussianMixture(n_components=3, random_state=42)
  gmm.fit(X_scaled)

  # Predict labels gốc (soft/hard assignment)
  labels_orig = gmm.predict(X_scaled)
  sil_orig = silhouette_score(X_scaled, labels_orig)
  print(f"Silhouette gốc: {sil_orig:.3f} (thấp nếu lộn xộn)")

  # Plot clusters gốc
  features_df['cluster_orig'] = labels_orig
  sns.scatterplot(data=features_df, x='actions', y='finalgrade', hue='cluster_orig')
  plt.title('Gốc Clusters Từ GMM')
  plt.show()
  ```
- **Output mong đợi**: Silhouette ~0.2-0.4 (gốc lộn xộn), plot scatter với 3 màu phân tách nhẹ.
- **Kiểm tra**: Nếu sil <0, thử n_components=2 hoặc features thêm (e.g., hour mean).

#### Step 3: Generate Synthetic Features/Users Với 3 Cụm (Sample Từ GMM)
- **Mô tả**: Sample x10 users từ GMM (2.3k), unscale để giữ range gốc. Assign labels dựa mean comp (giỏi: mean cao nhất).
- **Lý do**: Sample giữ mean/var/corr; x10 scale volume.
- **Code** (Tiếp theo Step 2):
  ```python
  # Generate synthetic
  n_synth = len(features_df) * 10
  X_synth_scaled, probs = gmm.sample(n_synth)  # probs: soft assignment
  X_synth = scaler.inverse_transform(X_synth_scaled)

  # DataFrame synthetic
  synth_df = pd.DataFrame(X_synth, columns=['actions', 'finalgrade'])
  synth_df['userid'] = range(10000, 10000 + n_synth)  # Synthetic IDs

  # Assign hard labels
  synth_df['cluster'] = np.argmax(probs, axis=1)
  cluster_means = synth_df.groupby('cluster')[['actions', 'finalgrade']].mean()
  sorted_clusters = cluster_means.mean(axis=1).sort_values(ascending=False).index
  cluster_names = {sorted_clusters[0]: 'giỏi', sorted_clusters[1]: 'khá', sorted_clusters[2]: 'yếu'}
  synth_df['group'] = synth_df['cluster'].map(cluster_names)

  # Validate clusters
  labels_synth = synth_df['cluster'].values
  sil_synth = silhouette_score(X_synth_scaled, labels_synth)
  print(f"Silhouette synthetic: {sil_synth:.3f} (>0.4: rõ ràng)")
  print("Phân bố nhóm:", synth_df['group'].value_counts())
  print("Corr synthetic:", synth_df['actions'].corr(synth_df['finalgrade']))

  # Plot
  sns.scatterplot(data=synth_df, x='actions', y='finalgrade', hue='group')
  plt.title('Synthetic Clusters (3 Nhóm)')
  plt.show()
  ```
- **Output mong đợi**: Sil ~0.5+ (rõ hơn gốc), corr ~0.75, ~770 users/nhóm (balanced weights).
- **Kiểm tra**: Nếu corr lệch >0.1, re-fit GMM với covariance_type='full'.

#### Step 4: Generate Synthetic Logs Từ Features (Rule-Based Bias Theo Cụm)
- **Mô tả**: Dùng probs gốc (80% viewed) cho events/actions, nhưng bias theo group (giỏi: tăng updated 20%). Số actions/user ~ NB (fit từ mean/var gốc). Time theo hourly probs.
- **Lý do**: Logs sequences; NB capture over-dispersion (var>>mean).
- **Code** (Tiếp theo Step 3; fit NB trước):
  ```python
  from scipy.stats import nbinom  # Negative Binomial

  # Fit NB cho actions (r, p từ mean/var gốc)
  mean_orig = user_actions.mean()  # 636.14
  var_orig = user_actions.var()    # 293456
  r_nb = mean_orig**2 / (var_orig - mean_orig)  # ~0.14 (low r = over-disp)
  p_nb = r_nb / (r_nb + mean_orig)
  print(f"NB params: r={r_nb:.2f}, p={p_nb:.4f}")

  # Probs gốc từ phân tích trước (hardcode từ output)
  probs_action = {'viewed': 0.801, 'updated': 0.068, 'graded': 0.038, 'uploaded': 0.028, 'created': 0.028, 'submitted': 0.018}  # Normalize nếu cần
  probs_hour = {11: 0.096, 12: 0.093, 13: 0.083, 16: 0.069, 15: 0.068}  # Top, fill rest uniform
  probs_hour = {h: probs_hour.get(h, 1/len(range(24))) for h in range(24)}  # Normalize

  # Generate logs
  synthetic_logs = []
  start_date = pd.Timestamp('2022-09-01')
  for _, row in synth_df.iterrows():
      num_actions = max(1, int(nbinom.rvs(r_nb, p_nb)))  # NB sample, min 1
      group = row['group']
      
      # Bias probs theo group
      if group == 'giỏi':
          probs_action_bias = probs_action.copy()
          probs_action_bias['updated'] += 0.20  # Tăng active
          probs_action_bias['viewed'] -= 0.10
      elif group == 'yếu':
          probs_action_bias = probs_action.copy()
          probs_action_bias['viewed'] += 0.10
          probs_action_bias['updated'] -= 0.05
      else:  # khá
          probs_action_bias = probs_action.copy()
      
      # Normalize bias probs
      total_bias = sum(probs_action_bias.values())
      probs_action_bias = {k: v/total_bias for k, v in probs_action_bias.items()}
      
      for _ in range(num_actions):
          action = np.random.choice(list(probs_action_bias.keys()), p=list(probs_action_bias.values()))
          eventname = '\\mod_assign\\event\\course_module_viewed' if action == 'viewed' else '\\mod_quiz\\event\\attempt_started'  # Map đơn giản
          hour = np.random.choice(list(probs_hour.keys()), p=list(probs_hour.values()))
          timecreated = start_date + pd.Timedelta(days=np.random.randint(365), hours=hour, minutes=np.random.randint(60))
          userid = row['userid']
          courseid = 670
          other = "{'assignid': '****'}" if np.random.rand() > 0.5 else np.nan
          
          synthetic_logs.append({
              'id': np.random.randint(9000000, 10000000),  # Fake ID
              'timecreated': timecreated,
              'eventname': eventname,
              'action': action,
              'target': 'course_module',
              'userid': userid,
              'courseid': courseid,
              'other': other
          })

  synth_logs_df = pd.DataFrame(synthetic_logs)
  print("Synthetic logs shape:", synth_logs_df.shape)
  synth_logs_df.to_csv('synthetic_logs.csv', index=False)
  ```
- **Output mong đợi**: ~140k rows, probs action bias (giỏi: updated ~27%).
- **Kiểm tra**: Counter(synth_logs_df['action']). Tỷ lệ ~80% viewed tổng.

#### Step 5: Generate Synthetic Grades Từ Features (Beta Cho Marginal)
- **Mô tả**: Assign finalgrade từ GMM, timemodified = timecreated cuối + random delay. Itemtype='course' fixed.
- **Lý do**: Giữ skewed (Beta fit mean=7.64, scale 0-10; -1 map to 0).
- **Code** (Tiếp theo Step 4):
  ```python
  # Fit Beta cho grades (scale 0-10, mean=7.64, var=2.95^2~8.7)
  # Method of moments: α = mean^2 * (scale-mean) / var * scale, β = α * (scale - mean) / mean
  scale = 10
  mean_g = 7.64  # Clip -1 to 0 trước fit
  var_g = (2.95)**2
  alpha = (mean_g**2 * (scale - mean_g)) / var_g
  beta = alpha * (scale - mean_g) / mean_g
  print(f"Beta params: α={alpha:.2f}, β={beta:.2f}")

  # Generate grades
  synth_grades = []
  for _, row in synth_df.iterrows():
      finalgrade = np.clip(stats.beta.rvs(alpha, beta, size=1)[0] * scale, 0, 10)  # Clip -1 equiv to 0
      timemodified = pd.Timestamp('2023-01-01') + pd.Timedelta(days=np.random.randint(1, 30))  # Random update
      synth_grades.append({
          'id': np.random.randint(300000, 400000),
          'timemodified': timemodified,
          'userid': row['userid'],
          'courseid': 670,
          'finalgrade': finalgrade[0],
          'itemtype': 'course'
      })

  synth_grades_df = pd.DataFrame(synth_grades)
  print("Synthetic grades shape:", synth_grades_df.shape)
  synth_grades_df.to_csv('synthetic_grades.csv', index=False)

  # Quick check
  print(f"Synthetic grades mean: {synth_grades_df['finalgrade'].mean():.2f}")
  ```
- **Output mong đợi**: ~2.3k rows, mean ~7.64.
- **Kiểm tra**: Hist so với gốc.

#### Step 6: Validation Tổng Thể (Fidelity & Clusters)
- **Mô tả**: Chạy tests so sánh gốc/synthetic (KS cho probs, Pearson corr, silhouette).
- **Lý do**: Đảm bảo <10% error (như Moreno paper).
- **Code** (Cuối):
  ```python
  # KS for action probs
  from scipy.stats import ks_2samp
  orig_actions = log_df['action'].value_counts(normalize=True)
  synth_actions = synth_logs_df['action'].value_counts(normalize=True)
  ks_stat, ks_p = ks_2samp(orig_actions.values, synth_actions.reindex(orig_actions.index, fill_value=0).values)
  print(f"Action KS p: {ks_p:.4f} (>0.05: giống)")

  # Corr synthetic
  synth_corr = synth_df['actions'].corr(synth_df['finalgrade'])
  print(f"Synth corr: {synth_corr:.3f} (gần 0.75)")

  # Silhouette
  print(f"Synth sil: {sil_synth:.3f}")

  # Plot so sánh grades
  fig, ax = plt.subplots(1, 2, figsize=(10,4))
  grades_df['finalgrade'].hist(ax=ax[0], alpha=0.7, label='Orig')
  synth_grades_df['finalgrade'].hist(ax=ax[1], alpha=0.7, label='Synth')
  ax[0].set_title('Orig Grades')
  ax[1].set_title('Synth Grades')
  plt.show()
  ```
- **Output mong đợi**: KS p>0.05, corr~0.75, sil>0.4.
- **Kiểm tra**: Nếu lệch, tune bias (e.g., +5% updated cho giỏi).

Hoàn tất! Chạy full notebook, bạn có synthetic CSV sẵn dùng (e.g., cho JMeter replay). Nếu error, debug Step 1. Muốn JMeter integrate (script JMX), hỏi thêm nhé! 😊