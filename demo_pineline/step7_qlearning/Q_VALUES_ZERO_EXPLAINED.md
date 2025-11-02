# 🔍 Giải Thích Vấn Đề Q-values = 0.0

## ❓ Tại sao Q-values đều = 0.0?

Khi bạn gọi API và nhận được recommendations với **tất cả q_value = 0.0**, có 3 nguyên nhân chính:

```json
"recommendations": [
    {
        "action_id": 64,
        "name": "bài kiểm tra bài 2 - hard",
        "q_value": 0.0  // ⚠️ Tại sao = 0?
    }
]
```

---

## 🔍 NGUYÊN NHÂN 1: State chưa có trong Q-table (Chính xác nhất)

### Giải thích:

**Q-Learning sử dụng tabular method:**
- Q-table lưu trữ: `{state_hash: {action_id: q_value}}`
- State được hash về tuple để làm key: `(0.6, 0.5, 0.0, 0.2, ...)`
- **Nếu state_hash chưa xuất hiện trong Q-table → tất cả Q-values = 0.0**

### Ví dụ cụ thể:

**Input features của bạn:**
```python
features = {
    "mean_module_grade": 0.6,
    "total_events": 0.9,
    "viewed": 0.5,
    ...
}
```

**Sau khi build_state() → state_vector:**
```python
state = [0.6, 0.467, 0.016, 0.0, 0.8, 0.5, 0.2, 0.0, 0.3, 0.8, 0.143, 0.67]
```

**Sau khi hash (state_decimals=1):**
```python
state_hash = (0.6, 0.5, 0.0, 0.0, 0.8, 0.5, 0.2, 0.0, 0.3, 0.8, 0.1, 0.7)
```

**Tìm trong Q-table:**
```python
if state_hash not in agent.q_table:
    # ❌ State này chưa được training!
    # → Tất cả Q-values = 0.0 (default)
```

### Code xử lý trong qlearning_agent.py:

```python
def recommend_action(self, state, available_actions, top_k=3, fallback_random=True):
    state_hash = self.hash_state(state)
    
    # Get Q-values từ Q-table
    q_values = [
        (action_id, self.q_table[state_hash][action_id])  # 👈 Nếu chưa có = 0.0
        for action_id in available_actions
    ]
    
    # Nếu tất cả Q-values = 0 → fallback to random
    if fallback_random and all(q == 0 for _, q in q_values):
        random_actions = random.sample(available_actions, min(top_k, len(available_actions)))
        return [(action_id, 0.0) for action_id in random_actions]  # 👈 Trả về random
```

---

## 🔍 NGUYÊN NHÂN 2: Model chưa được training đủ

### Thống kê từ output của bạn:

```json
"model_info": {
    "model_loaded": true,
    "n_states_in_qtable": 1816,      // 👈 Chỉ có 1816 states
    "total_updates": 30000,           // 👈 30k updates
    "episodes": 1000                  // 👈 1000 episodes
}
```

### Phân tích:

**1816 states trong Q-table** nghĩa là:
- Model chỉ "gặp" 1816 states khác nhau trong quá trình training
- Nhưng **không gian state là vô hạn** (continuous state space)
- State của sinh viên bạn **không nằm trong 1816 states này**

**Tỷ lệ coverage:**
```
Giả sử có ~10,000 sinh viên
→ Mỗi sinh viên có ~5-10 states khác nhau
→ Tổng states có thể có: 50,000 - 100,000

Coverage = 1816 / 50,000 = 3.6% ⚠️
→ 96.4% states chưa được học!
```

---

## 🔍 NGUYÊN NHÂN 3: State hashing làm mất thông tin

### Code hashing:

```python
def hash_state(self, state: np.ndarray) -> Tuple:
    return tuple(np.round(state, decimals=self.state_decimals))
    #                                     👆 default = 1
```

### Ví dụ:

**State gốc (12 chiều, precision cao):**
```python
[0.6000000238418579, 0.46666666865348816, 0.01600000075995922, ...]
```

**Sau khi round(decimals=1):**
```python
(0.6, 0.5, 0.0, 0.0, 0.8, 0.5, 0.2, 0.0, 0.3, 0.8, 0.1, 0.7)
```

**Vấn đề:**
- Nhiều states khác nhau được round thành **cùng 1 hash**
- Nhưng vẫn có **quá nhiều states unique** → Q-table không học hết
- State của sinh viên mới → chưa có trong Q-table

---

## ✅ GIẢI PHÁP

### 1. **Kiểm tra state có trong Q-table không**

Thêm logging vào `api_service.py`:

```python
@app.post('/api/recommend', response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    state = _build_state_from_request(req)
    
    # 👇 THÊM LOGGING
    if agent:
        state_hash = agent.hash_state(state)
        is_known_state = state_hash in agent.q_table
        
        print(f"[DEBUG] State hash: {state_hash}")
        print(f"[DEBUG] State known? {is_known_state}")
        
        if is_known_state:
            q_values = agent.q_table[state_hash]
            print(f"[DEBUG] Available Q-values: {len(q_values)} actions")
            print(f"[DEBUG] Max Q-value: {max(q_values.values()) if q_values else 0}")
        else:
            print(f"[DEBUG] State NOT in Q-table → Fallback to random")
    
    # ... rest of code
```

### 2. **Training thêm với states phổ biến**

Cần training model với nhiều **representative states** hơn:

```python
# Trong training script
# Generate diverse states covering common student profiles
def generate_diverse_states(n_samples=10000):
    profiles = {
        'struggling': {'mean_grade': (0.0, 0.4), 'engagement': (0.0, 0.3)},
        'average': {'mean_grade': (0.4, 0.7), 'engagement': (0.3, 0.7)},
        'excellent': {'mean_grade': (0.7, 1.0), 'engagement': (0.7, 1.0)}
    }
    # ... generate states covering all profiles
```

### 3. **Giảm state_decimals (Không khuyến khích)**

```python
# Thay đổi trong qlearning_agent.py
agent = QLearningAgent(
    n_actions=n_actions,
    state_decimals=0  # 👈 Round to integer (0.6 → 1.0)
)
```

**Hậu quả:**
- ✅ Giảm số states unique → tăng coverage
- ❌ Mất thông tin → recommendations kém chính xác

### 4. **Sử dụng Function Approximation (Tốt nhất)**

Thay vì tabular Q-learning, dùng **Deep Q-Network (DQN)**:

```python
# Neural network approximates Q(s, a)
class DQN:
    def __init__(self, state_dim=12, n_actions=100):
        self.model = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions)
        )
    
    def predict(self, state):
        # ✅ Có thể predict cho BẤT KỲ state nào
        return self.model(state)
```

**Ưu điểm:**
- ✅ Generalize cho unseen states
- ✅ Không cần lưu Q-table khổng lồ
- ✅ Q-values ≠ 0 cho mọi states

---

## 🧪 TEST & VERIFY

### 1. Kiểm tra Q-table coverage:

```python
# Test script
import pickle
from pathlib import Path

# Load model
model_path = Path('models/qlearning_model.pkl')
with open(model_path, 'rb') as f:
    data = pickle.load(f)

q_table = data['q_table']
print(f"Total states in Q-table: {len(q_table)}")

# Check sample states
sample_states = [
    (0.6, 0.5, 0.0, 0.0, 0.8, 0.5, 0.2, 0.0, 0.3, 0.8, 0.1, 0.7),
    (0.8, 0.9, 0.1, 0.1, 0.9, 0.8, 0.7, 0.2, 0.8, 0.9, 0.5, 0.9),
    (0.3, 0.2, 0.5, 0.0, 0.4, 0.3, 0.1, 0.0, 0.2, 0.4, 0.1, 0.3)
]

for state_hash in sample_states:
    if state_hash in q_table:
        print(f"✅ State {state_hash}: {len(q_table[state_hash])} actions learned")
    else:
        print(f"❌ State {state_hash}: NOT in Q-table")
```

### 2. Test với known state:

Tìm 1 state **có trong Q-table** để test:

```python
# Get first state from Q-table
first_state_hash = list(q_table.keys())[0]
print(f"Known state: {first_state_hash}")

# Test API với state này
response = requests.post('http://localhost:8080/api/recommend', json={
    'state': list(first_state_hash),  # Convert tuple → list
    'top_k': 5
})

result = response.json()
# Kiểm tra q_values có ≠ 0 không
print(result['recommendations'])
```

---

## 📊 KẾT LUẬN

### Vấn đề hiện tại:

```
Input state của sinh viên
    ↓
Build & hash state → (0.6, 0.5, 0.0, ...)
    ↓
Tìm trong Q-table (1816 states)
    ↓
❌ KHÔNG TÌM THẤY
    ↓
Fallback to random → q_value = 0.0
```

### Giải pháp ngắn hạn:
1. ✅ Add logging để confirm
2. ✅ Training thêm với diverse states

### Giải pháp dài hạn:
1. ✅ Chuyển sang DQN (Deep Q-Network)
2. ✅ Sử dụng state generalization
3. ✅ Hybrid: Q-learning + nearest neighbor fallback

---

## 🔗 Files cần chỉnh sửa

1. **api_service.py** - Add logging (line ~225)
2. **qlearning_agent.py** - Consider DQN
3. **train_qlearning.py** - Generate diverse training states
4. **state_builder.py** - Optimize state representation
