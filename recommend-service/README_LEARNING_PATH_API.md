# Learning Path API với Linear Regression

API này cung cấp hệ thống gợi ý lộ trình học tập thông minh sử dụng **Linear Regression** kết hợp với **Q-Learning** để tạo ra các đề xuất học tập được cá nhân hóa.

## 🎯 Tính năng chính

### 1. **Học máy Linear Regression**
- Dự đoán hiệu suất học tập dựa trên:
  - Cluster của học viên (Beginner/Intermediate/Advanced)
  - Trạng thái hiện tại (điểm số, tỷ lệ hoàn thành)
  - Độ khó của section
  - Sở thích học tập cá nhân

### 2. **Tối ưu hóa đa mục tiêu**
- **Performance**: Tối ưu kết quả học tập
- **Speed**: Tối ưu thời gian hoàn thành
- **Comprehensive**: Học tập toàn diện, sâu rộng

### 3. **Cá nhân hóa thông minh**
- Phân nhóm học viên theo năng lực
- Đề xuất hành động phù hợp với từng nhóm
- Ghi chú và tips học tập cá nhân

## 📋 API Endpoints

### 1. Tạo lộ trình học tập hoàn chỉnh

```http
POST /api/generate-learning-path
```

**Request Body:**
```json
{
    "userid": 123,
    "courseid": 5,
    "max_sections": 10,
    "include_completed": false,
    "optimization_goal": "performance"
}
```

**Response:**
```json
{
    "success": true,
    "user_id": 123,
    "course_id": 5,
    "total_sections": 5,
    "estimated_total_time_minutes": 150,
    "average_performance_score": 0.847,
    "optimization_goal": "performance",
    "learning_path": [
        {
            "section_id": 45,
            "section_name": "Section 45",
            "current_state": {
                "complete_rate": 0.600,
                "avg_score": 7.50,
                "completed": false
            },
            "recommended_actions": [
                {
                    "action": "attempt_new_quiz",
                    "predicted_performance": 0.8924,
                    "action_score": 0.9124,
                    "expected_complete_rate": 0.6,
                    "expected_score": 8,
                    "estimated_time_minutes": 25,
                    "difficulty_level": "Medium"
                }
            ],
            "priority_score": 0.9124,
            "predicted_performance": 0.8924,
            "estimated_time_minutes": 25,
            "difficulty_level": "Medium",
            "personalization_notes": [
                "Balanced approach recommended",
                "Complete more resources before attempting quizzes"
            ]
        }
    ],
    "model_info": {
        "algorithm": "Linear Regression + Q-Learning Hybrid",
        "user_cluster": 1,
        "cluster_description": "Intermediate - Balanced approach",
        "personalization_enabled": true,
        "model_version": "1.0"
    },
    "recommendations": {
        "study_tips": [
            "Balance between reviewing and learning new content",
            "Try different types of learning activities"
        ],
        "next_immediate_action": "attempt_new_quiz"
    }
}
```

### 2. Dự đoán hiệu suất cho section cụ thể

```http
POST /api/predict-performance
```

**Request Body:**
```json
{
    "userid": 123,
    "section_id": 45,
    "current_complete_rate": 0.6,
    "current_score": 7
}
```

**Response:**
```json
{
    "success": true,
    "user_id": 123,
    "section_id": 45,
    "predicted_performance": 0.8924,
    "current_state": {
        "complete_rate": 0.6,
        "score": 7
    },
    "user_cluster": 1,
    "performance_level": {
        "level": "High",
        "confidence": "High"
    },
    "predicted_at": "2025-09-27T10:30:00"
}
```

### 3. Phân tích học tập toàn diện

```http
POST /api/learning-analytics
```

**Request Body:**
```json
{
    "userid": 123,
    "courseid": 5
}
```

**Response:**
```json
{
    "success": true,
    "user_id": 123,
    "course_id": 5,
    "analytics": {
        "overall_progress": {
            "completed_sections": 3,
            "total_sections": 10,
            "completion_percentage": 30.0,
            "average_score": 7.2,
            "average_completion_rate": 0.65
        },
        "user_profile": {
            "cluster": 1,
            "learning_style": "Balanced and adaptive learner",
            "recommended_pace": "Moderate pace"
        },
        "performance_predictions": [
            {
                "section_id": 45,
                "predicted_performance": 0.892,
                "current_score": 7.5,
                "current_completion": 0.6
            }
        ],
        "recommendations": {
            "focus_areas": [
                "Review and strengthen understanding in sections: [23, 24, 25]"
            ],
            "study_tips": [
                "Balance between reviewing and learning new content"
            ]
        }
    }
}
```

### 4. Train model Linear Regression

```http
POST /api/train-model
```

**Response:**
```json
{
    "status": "success",
    "message": "Model trained successfully",
    "trained_at": "2025-09-27T10:30:00",
    "model_metrics": {
        "algorithm": "Linear Regression",
        "features_used": [
            "section_id",
            "cluster", 
            "current_complete_rate",
            "current_score",
            "difficulty_preference"
        ]
    }
}
```

## 🎯 Optimization Goals

### 1. **Performance** (Mặc định)
- Tối ưu hóa kết quả học tập
- Ưu tiên các hành động có hiệu suất cao nhất
- Cân bằng giữa thách thức và khả năng

### 2. **Speed** 
- Tối ưu hóa thời gian hoàn thành
- Ưu tiên các hành động nhanh chóng
- Tránh các hoạt động mất thời gian

### 3. **Comprehensive**
- Học tập toàn diện, sâu rộng
- Ưu tiên review và consolidation
- Tránh bỏ qua các bước quan trọng

## 🤖 Machine Learning Features

### Linear Regression Model
- **Input Features:**
  - Section ID (độ khó theo thứ tự)
  - User Cluster (0=Beginner, 1=Intermediate, 2=Advanced)
  - Current Complete Rate (0.0-1.0)
  - Current Score (0-10)
  - Difficulty Preference (0.0-1.0)

- **Output:**
  - Predicted Performance Score (0.0-1.0)

### User Clustering
- **Cluster 0 (Beginner):** Methodical, careful learner
- **Cluster 1 (Intermediate):** Balanced, adaptive learner  
- **Cluster 2 (Advanced):** Fast-paced, challenge-seeking learner

## 🚀 Cách sử dụng

### 1. Khởi động service
```bash
python app.py
```

### 2. Test API
```bash
python test_learning_path_api.py
```

### 3. Gọi API để tạo lộ trình học
```bash
curl -X POST http://127.0.0.1:8088/api/generate-learning-path \
-H "Content-Type: application/json" \
-d '{
    "userid": 123,
    "courseid": 5,
    "max_sections": 5,
    "optimization_goal": "performance"
}'
```

## 🔧 Cấu hình

Các tham số có thể điều chỉnh trong `config.py`:

```python
# Q-learning parameters
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9 
EXPLORATION_RATE = 0.2

# Discretization bins
SCORE_AVG_BINS = [0, 2, 4, 6, 8]
COMPLETE_RATE_BINS = [0.0, 0.3, 0.6]

# Available actions
ACTIONS = [
    'read_new_resource', 'review_old_resource',
    'attempt_new_quiz', 'redo_failed_quiz', 
    'skip_to_next_module', 'do_quiz_harder',
    'do_quiz_easier', 'do_quiz_same'
]
```

## 📊 Performance Metrics

Model được đánh giá qua:
- **MSE (Mean Squared Error)**: Sai số dự đoán
- **R² Score**: Độ chính xác của model
- **User Satisfaction**: Feedback từ người dùng thực tế

## 🔮 Future Enhancements

1. **Deep Learning**: Chuyển sang Neural Networks
2. **Reinforcement Learning**: Cải tiến Q-Learning
3. **Real-time Adaptation**: Cập nhật model theo thời gian thực
4. **Multi-objective Optimization**: Tối ưu đồng thời nhiều mục tiêu
5. **A/B Testing**: So sánh hiệu quả các thuật toán khác nhau