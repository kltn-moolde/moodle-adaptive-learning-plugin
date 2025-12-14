# Moodle Adaptive Learning Dashboard - API Integration Guide

## 📋 Overview

Dashboard này đã được tích hợp với Moodle Web Services API để fetch dữ liệu thực tế. Khi API call thất bại, hệ thống sẽ tự động fallback về mock data.

## 🔧 Setup Instructions

### 1. Cấu hình Moodle Web Services

Trên Moodle site của bạn, cần enable và cấu hình Web Services:

#### Bước 1: Enable Web Services
1. Đăng nhập với quyền admin
2. Vào **Site administration** → **Advanced features**
3. Check **Enable web services**
4. Click **Save changes**

#### Bước 2: Enable REST Protocol
1. Vào **Site administration** → **Server** → **Web services** → **Manage protocols**
2. Enable **REST protocol**

#### Bước 3: Tạo Web Service User
1. Tạo user mới hoặc dùng user hiện có
2. Gán role phù hợp (Teacher/Student)

#### Bước 4: Tạo Token
1. Vào **Site administration** → **Server** → **Web services** → **Manage tokens**
2. Click **Add**
3. Chọn user và service
4. Click **Save changes**
5. Copy token được tạo

### 2. Cấu hình Environment Variables

1. Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Cập nhật thông tin trong file `.env`:
```env
VITE_MOODLE_URL=https://your-moodle-site.com
VITE_MOODLE_TOKEN=your_token_here
```

**Lưu ý:** 
- `VITE_MOODLE_URL` không có trailing slash
- Token phải có đủ quyền để gọi các API functions

### 3. Cấu hình Web Service Functions

Dashboard cần các Moodle Web Service functions sau:

#### Core Functions (Bắt buộc)
- `core_webservice_get_site_info` - Lấy thông tin site và user hiện tại
- `core_user_get_users_by_field` - Lấy thông tin user
- `core_enrol_get_users_courses` - Lấy danh sách courses của user
- `core_enrol_get_enrolled_users` - Lấy danh sách học sinh trong course
- `core_course_get_contents` - Lấy nội dung course (modules, sections)
- `core_completion_get_activities_completion_status` - Lấy trạng thái hoàn thành

#### Grade Functions (Khuyến nghị)
- `gradereport_user_get_grade_items` - Lấy điểm số của học sinh

#### Log Functions (Tùy chọn)
- `core_course_get_recent_courses` - Lấy hoạt động gần đây

### 4. Cài đặt và Chạy

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 📊 Features Implemented

### Student Dashboard
- ✅ Lấy thông tin user từ `getSiteInfo()`
- ✅ Hiển thị avatar và tên thật từ Moodle
- ✅ Tính toán progress dựa trên completion status
- ✅ Hiển thị danh sách modules và trạng thái hoàn thành
- ✅ Chart tiến độ học tập theo thời gian
- ✅ Activity heatmap (mock nếu không có data)

### Teacher Dashboard
- ✅ Thống kê số lượng học sinh thực tế
- ✅ Tính toán active users hôm nay
- ✅ Average completion percentage
- ✅ Danh sách struggling topics (modules có completion thấp)
- ✅ Class performance chart
- ✅ Activity trends

### Student List (Teacher View)
- ✅ Danh sách học sinh từ `getEnrolledUsers()`
- ✅ Progress của từng học sinh
- ✅ Activity level dựa trên last access
- ✅ Trend indicators
- ✅ Filter và search functionality

### Course Analytics (Teacher View)
- ✅ Module view counts
- ✅ Resource type distribution
- ✅ Top performers ranking
- ✅ Weekly engagement patterns
- ✅ AI insights based on real data

## 🔄 Data Flow

```
1. Component Mount
   ↓
2. Call Moodle API
   ↓
3. Parse Response
   ↓
4. Update State
   ↓
5. Render UI
   ↓
6. If Error → Show Mock Data + Warning
```

## 🚨 Error Handling

Dashboard sử dụng graceful degradation:

1. **API Call Success**: Hiển thị data thực từ Moodle
2. **API Call Fail**: 
   - Show warning banner màu vàng
   - Fallback về mock data
   - Log error to console

## 🔍 API Functions Reference

### `getSiteInfo()`
Trả về thông tin site và user hiện tại.

### `getUserCourses(userId)`
Lấy danh sách courses mà user đã enroll.

### `getEnrolledUsers(courseId)`
Lấy danh sách tất cả users trong course (bao gồm students và teachers).

### `getCourseContent(courseId)`
Lấy cấu trúc course: sections, modules, activities.

### `getCourseCompletion(courseId, userId)`
Lấy completion status của từng module cho user.

### `getStudentProgress(courseId, userId)`
Tính toán overall progress, completed lessons, và grades.

### `getCourseStats(courseId)`
Tính toán thống kê: total students, active today, etc.

### `getAverageCompletion(courseId)`
Tính average completion percentage cho toàn class.

### `getStrugglingTopics(courseId)`
Tìm các topics mà nhiều học sinh chưa complete.

### `getModuleViews(courseId)`
Lấy view counts cho từng module (fallback về mock nếu không có data).

## 🎯 Best Practices

1. **Token Security**: Không commit `.env` file vào git
2. **Error Handling**: Luôn có fallback data
3. **Loading States**: Show loading indicators khi fetch data
4. **User Feedback**: Hiển thị error messages rõ ràng
5. **Performance**: Cache data khi có thể

## 🐛 Troubleshooting

### Issue: "Unable to load data from Moodle"
**Solutions:**
1. Kiểm tra MOODLE_URL và MOODLE_TOKEN trong `.env`
2. Verify token còn hiệu lực
3. Check CORS settings trên Moodle
4. Xem console logs để biết chi tiết lỗi

### Issue: "Network Error"
**Solutions:**
1. Kiểm tra kết nối internet
2. Verify Moodle site đang online
3. Check firewall/proxy settings

### Issue: "Invalid Token"
**Solutions:**
1. Tạo token mới trên Moodle
2. Verify token có đủ permissions
3. Check user có quyền access course không

### Issue: Empty Data
**Solutions:**
1. Verify user đã enroll vào course
2. Check course có modules/content chưa
3. Verify completion tracking được enable

## 📝 Notes

- Dashboard hiện tại sử dụng course đầu tiên của user
- Một số metrics (như view counts) có thể được mock nếu Moodle không track
- Activity heatmap hiện tại là mock data vì Moodle không có API trực tiếp
- Có thể extend để support multiple courses

## 🔐 Security Considerations

1. Token được lưu trong environment variables
2. Không expose token trong client-side code
3. Consider sử dụng backend proxy cho production
4. Implement rate limiting nếu cần

## 📚 Additional Resources

- [Moodle Web Services Documentation](https://docs.moodle.org/dev/Web_services)
- [Moodle API Functions](https://docs.moodle.org/dev/Web_service_API_functions)
- [Creating a Web Service Token](https://docs.moodle.org/en/Using_web_services)

## 🚀 Future Enhancements

- [ ] Add caching layer (localStorage/sessionStorage)
- [ ] Support multiple courses selection
- [ ] Real-time updates via WebSocket
- [ ] Export data to PDF/Excel
- [ ] Advanced analytics with AI insights
- [ ] Mobile responsive improvements
- [ ] Offline mode support
