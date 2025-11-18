# Quick Start - Moodle API Integration

## 🚀 Bắt đầu nhanh

### 1. Tạo file .env
```bash
cp .env.example .env
```

### 2. Cập nhật thông tin Moodle
Mở file `.env` và điền:
```env
VITE_MOODLE_URL=https://your-moodle-site.com
VITE_MOODLE_TOKEN=your_wstoken_here
```

### 3. Enable Web Services trên Moodle

**Cách lấy Token:**

1. Đăng nhập Moodle với quyền Admin
2. Vào: **Site administration** → **Server** → **Web services** → **Manage tokens**
3. Click **Add** để tạo token mới
4. Chọn user và service
5. Copy token được tạo

**Enable REST Protocol:**

1. Vào: **Site administration** → **Server** → **Web services** → **Manage protocols**
2. Enable **REST protocol**

**Enable Web Services:**

1. Vào: **Site administration** → **Advanced features**
2. Check **Enable web services**

### 4. Chạy ứng dụng
```bash
npm install
npm run dev
```

## ✅ Checklist

- [ ] Đã tạo file `.env`
- [ ] Đã điền `VITE_MOODLE_URL`
- [ ] Đã điền `VITE_MOODLE_TOKEN`
- [ ] Đã enable Web Services trên Moodle
- [ ] Đã enable REST protocol
- [ ] Token có quyền truy cập course
- [ ] User đã enroll vào ít nhất 1 course

## 📋 Required Moodle Functions

Dashboard cần các functions sau được enable:

- ✅ `core_webservice_get_site_info`
- ✅ `core_user_get_users_by_field`
- ✅ `core_enrol_get_users_courses`
- ✅ `core_enrol_get_enrolled_users`
- ✅ `core_course_get_contents`
- ✅ `core_completion_get_activities_completion_status`
- ✅ `gradereport_user_get_grade_items` (optional)

## 🔍 Test API Connection

Sau khi setup xong, mở browser console khi chạy app. Nếu thấy:
- ✅ Không có error → API hoạt động tốt
- ⚠️ Warning banner vàng → API fail, đang dùng mock data
- ❌ Error logs → Check lại cấu hình

## 💡 Tips

- **Token hết hạn?** Tạo token mới trên Moodle
- **CORS error?** Check Moodle có enable CORS chưa
- **Empty data?** Verify user đã enroll course
- **Permission error?** Token cần có đủ quyền

## 📖 Chi tiết

Xem file `MOODLE_INTEGRATION.md` để biết thêm chi tiết về:
- API functions reference
- Error handling
- Troubleshooting
- Security considerations
