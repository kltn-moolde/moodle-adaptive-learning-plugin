# Q-Learning AI Integration

## Tổng Quan

Tính năng Q-Learning AI được tích hợp vào FE-service-v2 để hiển thị:
- **Phân cụm học sinh** (Student Clusters)
- **Gợi ý học tập thông minh** (Smart Recommendations)
- **Thống kê Q-Table** (Q-Table Statistics)
- **Phân tích hành vi học tập** (Learning Behavior Analysis)

## API Endpoint

**Base URL:** `http://139.99.103.223:8088/api`

## Cấu Trúc Code

### 1. Service Layer
**File:** `src/services/qlearningService.ts`

Chứa các hàm gọi API:
- `getClusters()` - Lấy danh sách clusters
- `getClusterDetail(clusterId)` - Chi tiết một cluster
- `generateClusterProfile(clusterId)` - Tạo profile bằng LLM
- `getRecommendation(request)` - Lấy gợi ý học tập
- `getQTableStats()` - Thống kê Q-Table

### 2. UI Component
**File:** `src/pages/QLearningDashboard.tsx`

Dashboard hiển thị:
- **Q-Table Statistics** - 4 cards thống kê
  - Total States
  - Total Actions
  - Trained States
  - Coverage %

- **Student Clusters** - Grid 6 clusters
  - Cluster ID và tên
  - Số học sinh và tỷ lệ %
  - Click để xem chi tiết

- **Cluster Detail** - Chi tiết cluster được chọn
  - Thống kê cluster
  - Top 5 đặc điểm nổi bật (z-score)
  - Profile từ LLM (nếu có):
    - Điểm mạnh
    - Điểm yếu
    - Đề xuất giáo viên

- **Recommendation Form** - Form lấy gợi ý
  - Input: Student ID, Course ID
  - Output:
    - Trạng thái học tập (cluster, performance level)
    - Danh sách tài liệu đề xuất
    - Lý do và độ tin cậy

### 3. Navigation
**File:** `src/components/Navigation.tsx`

Thêm tab "Q-Learning AI" vào navbar cho tất cả user roles.

### 4. Routing
**File:** `src/App.tsx`

Thêm route `/qlearning` để render `QLearningDashboard`.

## Sử Dụng

### 1. Truy cập tính năng
- Đăng nhập vào hệ thống
- Click tab **"Q-Learning AI"** trên navbar
- Dashboard sẽ tự động load dữ liệu

### 2. Xem thông tin clusters
- 6 clusters hiển thị dạng grid
- Click vào cluster để xem chi tiết
- Chi tiết bao gồm:
  - Thống kê số lượng
  - Top 5 features nổi bật
  - Profile từ LLM (strengths, weaknesses, recommendations)

### 3. Lấy gợi ý học tập
- Nhập Student ID và Course ID
- Click "Lấy Gợi Ý"
- Kết quả hiển thị:
  - Cluster và performance level
  - Danh sách tài liệu được đề xuất
  - Lý do đề xuất và độ tin cậy

## API Response Examples

### 1. Get Clusters
```json
{
  "total_clusters": 6,
  "total_students": 1000,
  "clusters": [
    {
      "cluster_id": 0,
      "profile_name": "High Performers",
      "n_students": 200,
      "percentage": 20.0
    }
  ]
}
```

### 2. Get Cluster Detail
```json
{
  "cluster_id": 0,
  "statistics": {
    "n_students": 200,
    "percentage": 20.0,
    "top_features": [
      {
        "feature": "avg_grade",
        "z_score": 2.5,
        "interpretation": "Cao hơn trung bình"
      }
    ]
  },
  "existing_profile": {
    "profile_name": "High Performers",
    "description": "...",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "recommendations": ["..."]
  }
}
```

### 3. Get Recommendation
```json
{
  "student_id": 1,
  "course_id": 3,
  "recommendations": [
    {
      "resource_id": 5,
      "resource_name": "Advanced Topics",
      "confidence": 0.85,
      "reason": "Matches your learning pattern"
    }
  ],
  "learning_state": {
    "cluster_id": 2,
    "performance_level": "medium"
  },
  "metadata": {
    "algorithm": "Q-Learning",
    "timestamp": "2025-11-02T10:30:00Z"
  }
}
```

## Styling

Dashboard sử dụng Tailwind CSS với:
- **Primary colors:** Blue gradient
- **Cards:** White background với shadow
- **Icons:** Font Awesome
- **Responsive:** Grid layout responsive cho mobile/tablet/desktop

## Error Handling

- Connection errors → Hiển thị error banner màu đỏ
- API errors → Hiển thị message chi tiết
- Loading states → Spinner với text "Đang tải..."

## Future Enhancements

1. **Real-time Updates:** WebSocket để cập nhật real-time
2. **Export Reports:** Download PDF/Excel reports
3. **Filters:** Lọc clusters theo tiêu chí
4. **Charts:** Thêm biểu đồ visualization
5. **History:** Xem lịch sử recommendations

## Notes

- API endpoint hiện tại: `http://139.99.103.223:8088`
- Không có authentication (chưa implement)
- Tất cả users (Student, Instructor, Admin) đều có thể truy cập
- UI đơn giản, dễ thay đổi sau này
