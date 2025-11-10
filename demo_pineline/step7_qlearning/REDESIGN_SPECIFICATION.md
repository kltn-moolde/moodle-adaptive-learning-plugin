# Q-Learning System Redesign Specification
## Thiết kế lại hệ thống Q-Learning cho Adaptive Learning

**Date:** November 4, 2025  
**Status:** Design Document

---

## 1. STATE DESIGN (Thiết kế State)

### 1.1 State Structure
State được biểu diễn dưới dạng tuple 6 chiều:
```python
State = [cluster_id, current_module, module_progress, avg_score, recent_action, is_stuck]
```

### 1.2 State Components Specification

#### **Dimension 1: cluster_id** 
- **Values:** `[0, 1, 2, 3, 4, 5]` (6 clusters)
- **Source:** Cluster profiles từ `cluster_profiles.json`
- **Note:** Cluster gốc là 0-6 (7 clusters), nhưng loại bỏ cluster 3 (giáo viên)
  - Mapping: [0,1,2,4,5,6] → [0,1,2,3,4,5]
- **Rule-based reasoning:**
  - Phân loại dựa trên `mean_module_grade` và `total_events`
  - Mỗi cluster đại diện cho một nhóm học viên có đặc điểm học tập tương đồng
  - Cluster 3 (giáo viên) không phải là đối tượng học tập → loại bỏ

#### **Dimension 2: current_module**
- **Values:** `[0, 1, 2, ..., N-1]` (N là tổng số module trong khóa học)
- **Source:** Trích xuất từ `course_structure.json` → modules
- **Rule-based reasoning:**
  - Mỗi module đại diện cho một bài học/hoạt động trong khóa học
  - Thứ tự module phản ánh progression của khóa học
  - Từ course_structure.json, lọc các module có:
    - `visible = 1`
    - `uservisible = true`
    - Loại bỏ các module type không phải learning activity (subsection, label, etc.)
- **Expected count:** ~30 modules (theo yêu cầu "giả sử có 30 bài")

#### **Dimension 3: module_progress**
- **Values:** `[0.25, 0.5, 0.75, 1.0]` (4 bins - quartile binning)
- **Mapping:**
  - `0 - 25%` → 0.25
  - `25% - 50%` → 0.5
  - `50% - 75%` → 0.75
  - `75% - 100%` → 1.0
- **Source:** Tính từ số lượng events hoàn thành / tổng events trong module
- **Rule-based reasoning:**
  - Quartile binning giúp giảm state space nhưng vẫn giữ thông tin quan trọng
  - 4 mức đủ để phân biệt: mới bắt đầu, đang làm, gần xong, hoàn thành

#### **Dimension 4: avg_score**
- **Values:** `[0.25, 0.5, 0.75, 1.0]` (4 bins - quartile binning)
- **Mapping:**
  - `0 - 25%` → 0.25 (yếu)
  - `25% - 50%` → 0.5 (trung bình yếu)
  - `50% - 75%` → 0.75 (trung bình khá)
  - `75% - 100%` → 1.0 (giỏi)
- **Source:** Điểm trung bình từ các quiz/assignment đã hoàn thành
- **Rule-based reasoning:**
  - Điểm số phản ánh năng lực hiện tại của học viên
  - Chia 4 mức theo quartile để cân bằng phân phối

#### **Dimension 5: recent_action**
- **Values:** `[watch_video, do_quiz, mod_forum, review_quiz, read_resource, do_assignment]`
- **Source:** Phân tích từ `log.csv` - cột `eventname`, `component`, `action`
- **Action mapping rules:**

| recent_action | Moodle Events | Reasoning |
|---------------|---------------|-----------|
| `watch_video` | `\mod_hvp\event\course_module_viewed`<br>`\mod_video\event\course_module_viewed` | Xem nội dung video/interactive |
| `do_quiz` | `\mod_quiz\event\attempt_started`<br>`\mod_quiz\event\attempt_submitted` | Làm bài quiz/kiểm tra |
| `mod_forum` | `\mod_forum\event\course_module_viewed`<br>`\mod_forum\event\discussion_created` | Tham gia diễn đàn thảo luận |
| `review_quiz` | `\mod_quiz\event\attempt_reviewed`<br>`\mod_assign\event\feedback_viewed` | Xem lại kết quả/feedback |
| `read_resource` | `\mod_resource\event\course_module_viewed`<br>`\mod_page\event\course_module_viewed`<br>`\mod_url\event\course_module_viewed` | Đọc tài liệu/resource |
| `do_assignment` | `\mod_assign\event\assessable_submitted`<br>`\mod_assign\event\submission_form_viewed` | Làm bài tập/assignment |

- **Rule-based reasoning:**
  - Lấy 6 action đại diện phổ biến nhất (không lấy hết để tránh state space explosion)
  - Các action này cover các hoạt động chính: xem nội dung, làm bài, tương tác, ôn tập
  - Dựa trên tần suất trong log data để chọn actions có ý nghĩa

#### **Dimension 6: is_stuck**
- **Values:** `[0, 1]` (binary)
- **Calculation rule:**
  ```python
  is_stuck = 1 if:
    - Số lần thử lại quiz > threshold (e.g., 3 lần)
    - OR: Thời gian trên một module > ngưỡng (e.g., 2x median time)
    - OR: Điểm quiz liên tục thấp (< 50%)
  else:
    is_stuck = 0
  ```
- **Source:** Tính từ log data và grade data
- **Rule-based reasoning:**
  - Phát hiện học viên gặp khó khăn để can thiệp kịp thời
  - Dựa trên behavior patterns: retry nhiều, stuck lâu, điểm thấp

### 1.3 State Space Size
```
Total states = 6 (cluster) × 30 (module) × 4 (progress) × 4 (score) × 6 (action) × 2 (stuck)
             = 34,560 possible states
```

### 1.4 Scientific Justification (Chứng minh khoa học)

#### **Why this design?**

1. **Cluster-based personalization:**
   - Research shows students with similar learning behaviors benefit from similar interventions
   - Clustering reduces state space while maintaining personalization
   - Reference: [Intelligent Tutoring Systems literature]

2. **Module-level granularity:**
   - Fine-grained enough to track progress
   - Coarse-grained enough to avoid overfitting
   - Aligns with course design structure

3. **Quartile binning for continuous variables:**
   - Reduces noise from raw continuous values
   - Maintains ordinal relationships
   - Proven effective in educational data mining
   - Reference: Baker & Inventado (2014) - Educational Data Mining and Learning Analytics

4. **Recent action as memory:**
   - Markov assumption with one-step memory
   - Captures immediate context for next action recommendation
   - Balance between complexity and information

5. **Stuck detection:**
   - Early warning system for struggling students
   - Enables proactive intervention
   - Backed by learning analytics research on struggle detection

---

## 2. ACTION DESIGN (Thiết kế Action)

### 2.1 Action Structure
**Keep current design** - mỗi module/activity trong khóa học là một action

```python
Action = LearningAction(
    id=module_id,
    name=module_name,
    type=module_type,  # quiz, assign, resource, video, forum
    section=section_name,
    purpose=purpose,  # assessment, content, collaboration
    difficulty=difficulty  # easy, medium, hard
)
```

### 2.2 Action Space
- **Source:** `course_structure.json`
- **Size:** ~30-50 actions depending on course
- **Justification:**
  - Real learning activities that can be recommended
  - Directly actionable by students
  - Aligned with course structure

---

## 3. REWARD DESIGN (Thiết kế Reward)

### 3.1 Cluster-Specific Rewards
**Objective:** Thiết kế reward khác nhau cho từng cluster, phù hợp với đặc điểm học tập

### 3.2 Reward Formula

```python
def calculate_reward(cluster_id, action_outcome, state):
    cluster_level = get_cluster_level(cluster_id)  # weak, medium, strong
    base_reward = 0
    
    # Component 1: Completion reward (cluster-adaptive)
    if action_completed:
        if cluster_level == 'weak':
            base_reward += 10  # High reward for completion
        elif cluster_level == 'medium':
            base_reward += 7
        else:  # strong
            base_reward += 5  # Lower reward, expect more
    
    # Component 2: Score improvement (all clusters value this)
    score_delta = current_score - previous_score
    if score_delta > 0:
        base_reward += score_delta * 10  # Positive reinforcement
    
    # Component 3: Stuck penalty (stronger for weak clusters)
    if is_stuck:
        if cluster_level == 'weak':
            base_reward -= 3  # Need to guide away from stuck state
        else:
            base_reward -= 1
    
    # Component 4: Progression bonus (cluster-specific)
    if module_completed:
        if cluster_level == 'weak':
            base_reward += 5  # Encourage any progress
        elif cluster_level == 'medium':
            if action_difficulty == 'medium':
                base_reward += 7  # Right difficulty
        else:  # strong
            if action_difficulty == 'hard':
                base_reward += 10  # Challenge seekers
    
    # Component 5: Time efficiency (strong clusters value this)
    if cluster_level == 'strong':
        if completion_time < median_time:
            base_reward += 3  # Bonus for efficiency
    
    return base_reward
```

### 3.3 Cluster-Specific Reward Philosophy

| Cluster Type | Reward Strategy | Reasoning |
|--------------|----------------|-----------|
| **Weak** | High completion rewards<br>Encourage any progress<br>Strong stuck penalties | Need motivation and guidance<br>Small wins build confidence |
| **Medium** | Balanced rewards<br>Moderate difficulty preference<br>Score improvement focus | Standard progression<br>Build skills systematically |
| **Strong** | Challenge bonuses<br>Time efficiency rewards<br>High score expectations | Self-motivated<br>Seek mastery and efficiency |

### 3.4 Scientific Justification

1. **Differentiated rewards align with Zone of Proximal Development (Vygotsky)**
   - Weak clusters: need scaffolding → high completion rewards
   - Strong clusters: need challenge → difficulty bonuses

2. **Intrinsic vs Extrinsic motivation (Deci & Ryan, Self-Determination Theory)**
   - Weak: more extrinsic rewards needed
   - Strong: intrinsic motivation preserved through challenge

3. **Mastery learning principles (Bloom)**
   - All clusters ultimately aim for high scores
   - Different paths to mastery based on starting point

---

## 4. SIMULATION DESIGN (Thiết kế Simulation)

### 4.1 Simulation Process
```
1. Initialize synthetic students (from GMM or cluster profiles)
2. For each student:
   a. Assign to a cluster
   b. Set initial state: [cluster, module=0, progress=0.25, score=0.5, action=read_resource, stuck=0]
   c. Simulate learning trajectory:
      - Agent selects action based on ε-greedy policy
      - Student "performs" action → outcome (score, time, completion)
      - Calculate reward based on cluster
      - Update state
      - Repeat until course completion or max steps
3. Collect all (state, action, reward, next_state) tuples
4. Use for Q-learning training
```

### 4.2 Student Behavior Models (per cluster)
```python
class StudentSimulator:
    def __init__(self, cluster_id, cluster_profile):
        self.cluster = cluster_id
        self.profile = cluster_profile
        
        # Sample parameters from cluster distribution
        self.ability = sample_ability(cluster_profile)
        self.engagement = sample_engagement(cluster_profile)
        self.learning_rate = sample_learning_rate(cluster_profile)
    
    def perform_action(self, action, current_state):
        """Simulate student performing an action"""
        # Success probability depends on:
        # 1. Student ability
        # 2. Action difficulty
        # 3. Current score (knowledge level)
        
        success_prob = self.ability * (1 - action.difficulty) + current_state.avg_score * 0.3
        success = random.random() < success_prob
        
        # Generate outcome
        if success:
            score = random.uniform(0.7, 1.0)
            time = action.expected_time * random.uniform(0.8, 1.2)
        else:
            score = random.uniform(0.3, 0.6)
            time = action.expected_time * random.uniform(1.2, 2.0)
        
        return {
            'success': success,
            'score': score,
            'time': time,
            'completed': success
        }
```

---

## 5. VISUALIZATION REQUIREMENTS (Yêu cầu Visualization)

### 5.1 Learning Path Visualization
**Goal:** Visualize như "ô tô đi trên map" - theo dõi học sinh học như thế nào trong khóa học

#### 5.1.1 Individual Student Journey
```
Components:
1. Course map (2D layout of modules)
2. Student trajectory (animated path through modules)
3. State indicators at each step:
   - Progress bar
   - Score badge
   - Stuck indicator (red flag)
4. Time animation (playback student's journey)
```

#### 5.1.2 Visualization Types

**A. Path Visualization**
```
[Module 1] --> [Module 3] --> [Module 2] --> [Module 4] ...
    ↓             ↓              ↓             ↓
  Score: 0.8    Score: 0.6    Score: 0.9    Score: 0.7
  Time: 10min   Time: 25min   Time: 15min   Time: 20min
  Status: ✓     Status: ⚠     Status: ✓     Status: ✓
```

**B. Progress Heatmap**
```
Week 1  [██████░░░░] 60%  Score: 0.75
Week 2  [████████░░] 80%  Score: 0.82
Week 3  [██░░░░░░░░] 20%  Score: 0.45 ⚠ STUCK
Week 4  [██████████] 100% Score: 0.90
```

**C. State Transition Graph**
```
Cluster 0 → Module 5 (progress: 0.5, score: 0.75) 
  ↓
Cluster 0 → Module 6 (progress: 0.25, score: 0.75) 
  ↓
Cluster 0 → Module 6 (progress: 0.75, score: 0.8) [COMPLETED]
```

### 5.2 Implementation Tools
```python
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import networkx as nx

# 1. Interactive trajectory plot (Plotly)
def plot_student_journey(student_trajectory):
    """
    Interactive visualization of student path through course
    - X-axis: Time
    - Y-axis: Module ID
    - Color: Score
    - Size: Progress
    - Markers: Stuck events
    """
    pass

# 2. Heatmap of progress (Matplotlib/Seaborn)
def plot_progress_heatmap(student_trajectory):
    """
    2D heatmap showing progress across modules over time
    """
    pass

# 3. Network graph of transitions (NetworkX)
def plot_state_transitions(trajectory):
    """
    Directed graph showing state transitions
    Nodes: States
    Edges: Actions taken
    """
    pass
```

### 5.3 Visualization Features

1. **Real-time animation**
   - Play/Pause/Speed control
   - Step-by-step navigation

2. **Comparison view**
   - Compare multiple students
   - Compare with optimal path
   - Compare across clusters

3. **Metrics overlay**
   - Progress percentage
   - Current score
   - Time spent
   - Actions taken
   - Stuck events count

4. **Export capabilities**
   - Save as HTML (interactive)
   - Save as MP4 (video)
   - Save as PNG (snapshot)

---

## 6. API OUTPUT (Keep Existing)

### 6.1 Existing API Endpoints (Preserve)
```
POST /recommend
POST /batch-recommend
GET /qtable-info
GET /cluster-info
GET /state-info
```

### 6.2 Output Format (No Change)
```json
{
  "student_id": "123",
  "current_state": {...},
  "recommended_actions": [
    {
      "action_id": 67,
      "action_name": "Quiz: Variables and Data Types",
      "q_value": 8.5,
      "reasoning": "Cluster 2 students benefit from this quiz at current progress level"
    }
  ]
}
```

---

## 7. UTILITY APIs (Keep Existing)

### 7.1 Q-Table Information
- `GET /qtable/summary` - Tổng quan Q-table
- `GET /qtable/states` - Danh sách states
- `GET /qtable/positive-q` - States có Q-values dương

### 7.2 Cluster Information  
- `GET /cluster/profiles` - Thông tin các clusters
- `GET /cluster/{id}/stats` - Thống kê cluster cụ thể

### 7.3 Debugging & Analysis
- `GET /debug/state-lookup` - Tra cứu state
- `GET /debug/coverage` - Coverage analysis

---

## 8. IMPLEMENTATION PRIORITY

### Phase 1: Core Redesign (Week 1-2)
1. ✅ Redesign `state_builder.py` với 6-dim state
2. ✅ Redesign `reward_calculator.py` với cluster-specific rewards
3. ✅ Update `action_space.py` (minimal changes)
4. ✅ Implement quartile binning utility
5. ✅ Implement stuck detection logic

### Phase 2: Simulation (Week 3)
1. ✅ Redesign `simulator.py` với new state/reward
2. ✅ Generate synthetic data với new format
3. ✅ Train Q-learning với new data
4. ✅ Validate Q-table quality

### Phase 3: Visualization (Week 4)
1. ✅ Implement path visualization
2. ✅ Implement progress heatmap
3. ✅ Implement state transition graph
4. ✅ Add animation & interactivity

### Phase 4: Integration & Testing (Week 5)
1. ✅ Update API endpoints
2. ✅ Integration testing
3. ✅ Performance optimization
4. ✅ Documentation

---

## 9. SUCCESS METRICS

1. **State Coverage:** >70% of states visited during simulation
2. **Q-value Convergence:** Q-values stabilize after training
3. **Cluster Differentiation:** Different clusters show different optimal policies
4. **Recommendation Quality:** Students in test set show score improvement when following recommendations
5. **Visualization Usability:** Stakeholders can understand student journeys

---

## 10. RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| State space too large | High computation | Use state aggregation if needed |
| Insufficient real data | Medium | Augment with realistic simulation |
| Cluster profiles inaccurate | High | Validate clusters with domain experts |
| Visualization performance | Low | Use sampling for large datasets |

---

## APPENDIX A: Data Sources

- `data/log/log.csv` - Raw Moodle logs
- `data/log/grade.csv` - Grade data
- `data/course_structure.json` - Course modules
- `data/cluster_profiles.json` - Cluster characteristics
- `data/synthetic_students_gmm.csv` - Synthetic student data

---

## APPENDIX B: Key References

1. **Reinforcement Learning in Education:**
   - Mandel et al. (2014) - Offline Policy Evaluation with RL
   - Barnes & Stamper (2010) - Intelligent Tutoring Systems

2. **Learning Analytics:**
   - Baker & Inventado (2014) - Educational Data Mining
   - Siemens & Gasevic (2012) - Learning Analytics

3. **Adaptive Learning:**
   - VanLehn (2011) - The Relative Effectiveness of Human Tutoring
   - Aleven et al. (2016) - Instruction Based on Adaptive Learning Technologies

---

**End of Specification**
