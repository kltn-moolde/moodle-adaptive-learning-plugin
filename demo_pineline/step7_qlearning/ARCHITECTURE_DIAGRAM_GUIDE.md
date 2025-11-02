# Giải thích Sơ đồ Kiến trúc (architecture_diagram.svg)

## 📊 Tổng quan

Sơ đồ mô tả luồng dữ liệu và xử lý từ **Moodle raw data** → **GMM clustering** → **Q-Learning training** → **API recommendation**.

---

## 🔄 Các Phase trong Kiến trúc

### **Phase 1: Dữ liệu Moodle (Data Source)**
- **Input**: Dữ liệu thô từ Moodle
  - `grade.csv`: Điểm số của sinh viên
  - `log.csv`: Logs hoạt động (viewed, submitted, etc.)
- **Vị trí**: `step7_qlearning/data/log/`
- **Số lượng**: ~24 sinh viên thật

### **Phase 2: Moodle Analytics Pipeline**
Xử lý dữ liệu qua 5 bước:

1. **Feature Extraction** (`core/feature_extractor.py`)
   - Trích xuất features từ grades + logs
   - Normalize features (MinMax/Z-score)

2. **Feature Selection** (`core/feature_selector.py`)
   - Loại bỏ features có variance thấp
   - Loại bỏ features có correlation cao
   - Chọn ~15 features tối ưu

3. **Optimal Clustering** (`core/optimal_cluster_finder.py`)
   - Thử k = 2-10 clusters
   - Tính BIC, AIC, Silhouette score
   - Chọn k tối ưu (thường là 6)

4. **Cluster Profiling** (`core/cluster_profiler.py`)
   - Tạo profile cho mỗi cluster
   - **Sử dụng LLM** để mô tả đặc điểm cluster (excellent, good, average, struggling, at-risk)
   - Lưu `cluster_profiles.json`

5. **Sinh Synthetic Students** (`core/gmm_data_generator.py`)
   - Dùng GMM để sinh 200 sinh viên synthetic
   - Mỗi student có `cluster_id` (0-5)
   - Lưu `synthetic_students_gmm.csv`

**Output**:
- `outputs/gmm_generation/synthetic_students_gmm.csv`
- `outputs/cluster_profiling/cluster_profiles.json`
- `data/course_structure.json`

### **Phase 3: Sync Data**
- **Script**: `sync_pipeline_data.py`
- **Chức năng**: Copy files từ `moodle_analytics_pipeline/outputs/` sang `step7_qlearning/data/`
- Đảm bảo Q-Learning có input data mới nhất

### **Phase 4: Q-Learning System**

Huấn luyện agent qua 4 bước:

1. **Simulate Learning** (`simulate_learning_data.py`)
   - Load synthetic students
   - Mô phỏng quá trình học (episodes)
   - Sinh learning logs

2. **Build States & Actions** (`core/state_builder.py`, `core/action_space.py`)
   - State: Vector đại diện trạng thái học sinh (features + cluster_id)
   - Action: Các hành động gợi ý (study more, review, take quiz, etc.)

3. **Calculate Rewards** (`core/reward_calculator.py`)
   - Reward dựa trên: grade improvement, engagement, completion
   - Cluster-specific rewards (cluster tốt/yếu có reward khác nhau)

4. **Train Q-Learning Agent** (`core/qlearning_agent.py`)
   - Học Q-table: `Q(state, action) → value`
   - Epsilon-greedy exploration
   - Lưu model

**Output**:
- `models/qlearning_model.pkl` (Q-table + metadata)

### **Phase 5: API Service**
- **File**: `api_service.py` (FastAPI)
- **Endpoint**: `POST /recommend`

**Flow**:
1. Load `cluster_profiles.json`
2. Nhận `student_features` từ client
3. **Predict cluster_id** (distance matching với cluster means)
4. Query Q-table để lấy best action
5. Return recommendations

**Input example**:
```json
{
  "student_features": {
    "mean_module_grade": 0.75,
    "total_events": 0.6,
    "viewed": 0.7,
    "submitted": 0.6,
    ...
  }
}
```

**Output example**:
```json
{
  "action": "study_more",
  "confidence": 0.85,
  "cluster_id": 2,
  "cluster_description": "Good performance with..."
}
```

### **Phase 6: Client Request**
- Client gửi student features
- Nhận recommendations từ API
- Hiển thị gợi ý cho sinh viên

---

## 📁 Cấu trúc File tương ứng

### `moodle_analytics_pipeline/`
```
core/
  ├── feature_extractor.py      # Phase 2.1
  ├── feature_selector.py        # Phase 2.2
  ├── optimal_cluster_finder.py  # Phase 2.3
  ├── cluster_profiler.py        # Phase 2.4
  └── gmm_data_generator.py      # Phase 2.5

outputs/
  ├── gmm_generation/
  │   └── synthetic_students_gmm.csv
  └── cluster_profiling/
      └── cluster_profiles.json
```

### `step7_qlearning/`
```
core/
  ├── state_builder.py         # Phase 4.2
  ├── action_space.py          # Phase 4.2
  ├── reward_calculator.py     # Phase 4.3
  └── qlearning_agent.py       # Phase 4.4

data/
  ├── log/ (grade.csv, log.csv)        # Phase 1
  ├── synthetic_students_gmm.csv       # From pipeline
  ├── cluster_profiles.json            # From pipeline
  └── course_structure.json

models/
  └── qlearning_model.pkl       # Phase 4 output

api_service.py                  # Phase 5
sync_pipeline_data.py           # Phase 3
simulate_learning_data.py       # Phase 4.1
```

---

## 🎨 Màu sắc trong Sơ đồ

- **🔴 Hồng (box-data)**: Dữ liệu gốc
- **🔵 Xanh dương (box-primary)**: Pipeline xử lý/phân tích
- **🟢 Xanh lá (box-success)**: Output/Model đã train
- **🟠 Cam (box-warning)**: Sync data/API service
- **🟣 Tím (box-info)**: Q-Learning system

---

## 🚀 Cách sử dụng Sơ đồ

### 1. Xem trực tiếp trong VS Code
- Mở file `architecture_diagram.svg`
- VS Code sẽ preview SVG tự động
- Zoom in/out để xem chi tiết

### 2. Xuất sang PNG (nếu cần)
```bash
# Dùng Inkscape (cần cài đặt)
inkscape architecture_diagram.svg --export-png=architecture_diagram.png --export-width=2000

# Hoặc dùng ImageMagick
convert -density 300 architecture_diagram.svg architecture_diagram.png
```

### 3. Chỉnh sửa (nếu muốn)
- **Draw.io/diagrams.net**: Import SVG → chỉnh sửa → Export
- **Figma**: Import SVG → edit
- **Inkscape**: Mở SVG → chỉnh sửa trực tiếp

### 4. Embed vào Documentation
```markdown
![Architecture Diagram](./architecture_diagram.svg)
```

---

## 🔗 Tài liệu liên quan

- `PIPELINE_INTEGRATION.md`: Chi tiết tích hợp giữa 2 dự án
- `README.md`: Hướng dẫn chạy từng component
- `moodle_analytics_pipeline/README.md`: Chi tiết về GMM pipeline

---

## 📝 Notes

- Sơ đồ được tạo bằng SVG thuần (không phụ thuộc external tools)
- Có thể view/edit trực tiếp trong browser hoặc VS Code
- Màu sắc và layout được tối ưu cho in ấn và presentation
- Các label tiếng Việt để dễ hiểu cho người Việt

---

**Tạo bởi**: GitHub Copilot  
**Ngày**: 2025-11-02  
**Version**: 1.0
