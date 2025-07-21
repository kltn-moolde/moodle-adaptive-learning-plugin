-- Moodle Table Relationship Notes (short version) --

-- mdl_course: Khóa học
-- - id: khóa chính
-- - fullname, shortname: tên khóa học

-- mdl_course_sections: Các phần (section) trong khóa học
-- - id: khóa chính
-- - course: FK -> mdl_course.id
-- - section: số thứ tự (0 = tổng quan)
-- - name: tên section

-- mdl_course_modules: Các module (resource, lesson, etc.) trong section
-- - id: khóa chính
-- - course: FK -> mdl_course.id
-- - module: FK -> mdl_modules.id
-- - instance: ID bản ghi trong bảng module tương ứng (vd: mdl_resource.id)
-- - section: FK -> mdl_course_sections.id

-- mdl_modules: Danh sách loại module (resource, lesson, quiz, etc.)
-- - id: khóa chính
-- - name: tên module ('resource', 'lesson', ...)

-- mdl_resource / mdl_lesson / mdl_label / ...: Dữ liệu chi tiết cho từng loại module
-- - id: khóa chính
-- - name: tiêu đề nội dung
-- - intro: mô tả

-- mdl_tag: Danh sách tag
-- - id: khóa chính
-- - name: tên tag

-- mdl_tag_instance: Gắn tag với đối tượng
-- - id: khóa chính
-- - tagid: FK -> mdl_tag.id
-- - component: ví dụ 'mod_resource'
-- - itemid: ID trong bảng gốc (vd: mdl_resource.id)
-- - contextid: FK -> mdl_context.id

-- mdl_user: Người dùng
-- - id: khóa chính
-- - username, firstname, lastname, email

-- mdl_logstore_standard_log: Log mặc định của Moodle (hoạt động của người dùng)
-- - id: khóa chính
-- - userid: FK -> mdl_user.id
-- - courseid: FK -> mdl_course.id
-- - contextinstanceid: tùy loại hoạt động (vd: quiz.id, resource.id)
-- - component: ví dụ 'mod_resource'
-- - action: hành động (viewed, updated, etc.)
-- - target: đối tượng (course, module, user, etc.)
-- - timecreated: timestamp
-- - origin: 'web', 'cli', etc.