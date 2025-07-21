-- Mối quan hệ giữa các bảng liên quan đến khóa học (Course Structure) --

-- 1 khóa học (mdl_course)
-- -> có nhiều phần (section)     => Quan hệ: 1 course -> N section

-- mdl_course_sections
-- - course         FK -> mdl_course.id
-- - section        số thứ tự (0 = tổng quan)
-- - id             dùng làm FK cho course_modules

-- 1 section (mdl_course_sections)
-- -> chứa nhiều module            => Quan hệ: 1 section -> N module (course_modules)

-- mdl_course_modules
-- - section        FK -> mdl_course_sections.id
-- - module         FK -> mdl_modules.id
-- - instance       FK -> bảng module tương ứng (vd: mdl_resource.id)

-- 1 course_module (mdl_course_modules)
-- -> là "vỏ bọc" cho module cụ thể như resource, lesson, quiz, etc.
-- -> được định danh qua 'instance' và 'module'

-- mdl_modules
-- - id             định danh loại module (resource, lesson, quiz, ...)
-- - name           ví dụ: 'resource', 'quiz', ...

-- Ví dụ:
-- - course.id = 4
-- - section.id = 19 (thuộc course 4)
-- - course_module.id = 123 (thuộc section 19)
-- - module = 17 → tra mdl_modules → 'resource'
-- - instance = 5 → tra mdl_resource.id = 5