# PHASE 1: Hệ thống AI Gợi ý Học tập Thông minh

## 🎯 Tổng quan

Phase 1 tập trung vào việc **mở rộng và cải thiện mô hình Q-Learning hiện có** để tạo ra một hệ thống AI gợi ý học tập thông minh với khả năng cá nhân hóa sâu. Dựa trên phân tích dữ liệu thực tế từ Moodle, hệ thống được thiết kế để hiểu rõ hành vi học tập của từng sinh viên và đưa ra gợi ý phù hợp.

## 📊 Dữ liệu đầu vào

- **File**: `features_scaled_report.json`
- **Số sinh viên**: 15
- **Số features**: 70+ (các events từ Moodle)
- **Các loại events chính**:
  - Assignment events (view, submit, feedback)
  - Quiz events (attempt, submit, review)
  - Resource events (view, download)
  - Course events (view, progress tracking)
  - Interaction events (discussion, comments)

## 🏗️ Kiến trúc hệ thống

### 1. **Learning States (18 trạng thái)**
```python
# Trạng thái cơ bản
VIEW_COURSE, VIEW_MODULE, VIEW_RESOURCE

# Trạng thái Assignment
VIEW_ASSIGNMENT, START_ASSIGNMENT, SUBMIT_ASSIGNMENT, VIEW_FEEDBACK

# Trạng thái Quiz  
VIEW_QUIZ, START_QUIZ, SUBMIT_QUIZ, REVIEW_QUIZ

# Trạng thái tương tác
VIEW_GRADES, VIEW_PROGRESS, PARTICIPATE_DISCUSSION, DOWNLOAD_MATERIALS

# Trạng thái đặc biệt
SEEK_HELP, REVIEW_MISTAKES, PLAN_STUDY
```

### 2. **Student Profile System**
```python
@dataclass
class StudentProfile:
    user_id: int
    cluster_id: int
    learning_style: LearningStyle  # visual, auditory, kinesthetic, reading_writing
    performance_level: PerformanceLevel  # excellent, good, average, below_avg, poor
    engagement_score: float
    completion_rate: float
    time_preference: str
    weak_areas: List[str]
    strong_areas: List[str]
    learning_goals: List[str]
    current_state: LearningState
    learning_history: List[LearningState]
    performance_trend: str
```

### 3. **Enhanced Q-Learning Agent**
- **Q-table chính**: Học chiến lược tổng quát
- **Context-specific Q-tables**:
  - `help_q_table`: Khi sinh viên cần hỗ trợ
  - `excellent_q_table`: Khi sinh viên học tốt
  - `struggling_q_table`: Khi sinh viên gặp khó khăn
- **Adaptive epsilon**: Điều chỉnh exploration dựa trên performance

### 4. **Enhanced Reward System**
```python
total_reward = (base_reward * performance_multiplier * learning_style_multiplier + 
               engagement_bonus + completion_bonus + 
               context_bonus + progress_bonus - difficulty_penalty)
```

**Các yếu tố reward**:
- **Base reward**: Giá trị cơ bản của hoạt động
- **Performance multiplier**: Điều chỉnh theo mức độ hiệu suất
- **Learning style multiplier**: Điều chỉnh theo phong cách học
- **Engagement bonus**: Thưởng dựa trên mức độ tham gia
- **Completion bonus**: Thưởng dựa trên tỷ lệ hoàn thành
- **Progress bonus**: Thưởng khi tiến bộ (không lặp state)
- **Difficulty penalty**: Phạt khi chuyển đổi quá nhanh

## 🤖 Hệ thống Gợi ý Thông minh

### **IntelligentRecommendationSystem**
Tạo gợi ý cá nhân hóa dựa trên:
1. **Context detection**: Xác định tình huống hiện tại
2. **Policy selection**: Chọn Q-table phù hợp
3. **Confidence scoring**: Tính độ tin cậy
4. **Reasoning generation**: Tạo lý do cho gợi ý
5. **Benefit estimation**: Ước tính lợi ích
6. **Time estimation**: Ước tính thời gian cần thiết

### **LearningRecommendation**
```python
@dataclass
class LearningRecommendation:
    student_id: int
    recommended_state: LearningState
    confidence_score: float
    reasoning: str
    expected_benefit: float
    time_estimate: int  # phút
    difficulty_level: str
    prerequisites: List[LearningState]
```

## 📈 Các tính năng chính

### 1. **Phân tích dữ liệu nâng cao**
- Tự động suy luận learning style từ hành vi
- Xác định performance level dựa trên điểm số
- Phát hiện weak/strong areas
- Tạo enhanced features từ dữ liệu gốc

### 2. **Cá nhân hóa sâu**
- Profile cá nhân chi tiết cho mỗi sinh viên
- Điều chỉnh chiến lược dựa trên đặc điểm cá nhân
- Context-aware recommendations
- Adaptive learning parameters

### 3. **Hệ thống reward thông minh**
- Multi-factor reward calculation
- Performance-based adjustments
- Learning style preferences
- Progress tracking và penalties

### 4. **Gợi ý thông minh**
- Real-time recommendations
- Confidence scoring
- Detailed reasoning
- Prerequisites checking
- Time và difficulty estimation

## 🚀 Cách sử dụng

### **Chạy demo**
```bash
cd step999_test
python demo_phase1.py
```

### **Sử dụng trong code**
```python
from phase1_enhanced_learning_system import *

# 1. Xử lý dữ liệu
processor = DataProcessor("data/features_scaled_report.json")
processor.create_enhanced_features()
student_profiles = processor.create_student_profiles()

# 2. Khởi tạo hệ thống
reward_system = EnhancedRewardSystem()
q_agents = {i: EnhancedQLearningAgent(...) for i in range(3)}
recommendation_system = IntelligentRecommendationSystem(q_agents, reward_system)

# 3. Tạo gợi ý
recommendation = recommendation_system.get_personalized_recommendation(student_profile)
```

## 📊 Kết quả mong đợi

### **Input**: Dữ liệu Moodle events
### **Output**: 
- **Student profiles** với thông tin cá nhân hóa
- **Learning recommendations** chi tiết
- **Confidence scores** cho mỗi gợi ý
- **Reasoning** giải thích tại sao gợi ý này phù hợp
- **Time estimates** và difficulty levels

### **Ví dụ output**:
```
🎯 GỢI Ý CÁ NHÂN HÓA:
   📚 Hoạt động: submit_assignment
   🎯 Độ tin cậy: 0.85
   💡 Lý do: Dựa trên hiệu suất hiện tại, bạn nên tập trung vào các hoạt động cơ bản. 
            Phong cách học tập trực quan của bạn phù hợp với hoạt động này.
   📈 Lợi ích dự kiến: 0.95
   ⏱️  Thời gian: 45 phút
   📊 Độ khó: Khó
   🔗 Prerequisites: ['view_assignment', 'start_assignment']
```

## 🔄 So sánh với hệ thống cũ

| Tính năng | Hệ thống cũ | Phase 1 |
|-----------|-------------|---------|
| Số states | 6 | 18 |
| Cá nhân hóa | Cơ bản (cluster) | Sâu (profile chi tiết) |
| Reward system | Đơn giản | Multi-factor |
| Context awareness | Không | Có (3 contexts) |
| Reasoning | Không | Có (detailed) |
| Time estimation | Không | Có |
| Prerequisites | Không | Có |

## 🎯 Chuẩn bị cho Phase 2

Phase 1 tạo nền tảng vững chắc cho Phase 2 với:
- ✅ **Enhanced data processing**
- ✅ **Detailed student profiling**
- ✅ **Context-aware Q-learning**
- ✅ **Intelligent recommendation system**
- ✅ **Multi-factor reward system**

**Phase 2 sẽ tập trung vào**:
- Real-time recommendation engine
- Adaptive learning path generator
- Performance monitoring system
- Mobile app interface
- Integration với LMS hiện có

## 📁 Cấu trúc files

```
step999_test/
├── phase1_enhanced_learning_system.py  # Code chính Phase 1
├── demo_phase1.py                      # Demo và test
├── README_PHASE1.md                    # Tài liệu này
├── phase1_demo_visualization.png       # Biểu đồ demo
└── data/
    └── features_scaled_report.json     # Dữ liệu đầu vào
```

## 🛠️ Dependencies

```python
numpy
pandas
matplotlib
seaborn
scikit-learn
```

## 📝 Ghi chú

- Hệ thống được thiết kế để dễ dàng mở rộng và tùy chỉnh
- Có thể điều chỉnh các tham số reward và learning
- Hỗ trợ thêm learning styles và performance levels mới
- Tương thích với dữ liệu Moodle hiện có
