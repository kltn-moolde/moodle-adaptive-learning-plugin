SELECT * FROM moodle.mdl_course; -- Lấy danh sách khóa học
SELECT * FROM moodle.mdl_course_sections; -- Lấy danh sách các phần trong khóa học
SELECT * FROM moodle.mdl_course_modules; -- Lấy danh sách các mô-đun trong khóa học
SELECT * FROM moodle.mdl_modules; -- Lấy danh sách các mô-đun
SELECT * FROM moodle.mdl_lesson; -- Lấy danh sách các bài học
SELECT * FROM moodle.mdl_lesson_pages; -- Lấy danh sách các trang bài học
SELECT * FROM moodle.mdl_resource; -- Lấy danh sách các tài nguyên
SELECT * FROM moodle.mdl_logstore_standard_log; -- Lấy danh sách các log
SELECT * FROM moodle.mdl_label; -- Lấy danh sách các nhãn -- video
SELECT * FROM moodle.mdl_tag_instance; -- Lấy danh sách các tag instance
SELECT * FROM moodle.mdl_tag; -- Lấy danh sách các tag
SELECT * FROM moodle.mdl_user; -- Lấy danh sách người dùng
-- Danh sách các bảng đã nắm rõ - hay dùng
 

-- LẤY các LO của 1 course kèm theo tag dok (loại trừ module không phải là subsection hoặc forum)
-- chỉnh lại cm.course = 4 nếu cần lấy cho khóa học khác
SELECT 
    cm.id AS course_module_id,
    cm.module,
    m.name AS modname,
    cm.instance,
    t.name AS tag_name
FROM mdl_course_modules cm
JOIN mdl_modules m ON cm.module = m.id
LEFT JOIN mdl_tag_instance ti ON ti.itemid = cm.id
LEFT JOIN mdl_tag t ON t.id = ti.tagid
WHERE cm.course = 4 and cm.module != 20 and cm.module != 8 -- loại trừ subsection và forum



-- LẤY log của user cụ thể
-- chỉnh lại l.userid = 4 nếu cần lấy cho user khác
SELECT *
        FROM mdl_logstore_standard_log l
        WHERE l.userid = 4
        ORDER BY l.timecreated DESC   



-- LẤY log của user cụ thể trong 1 khoá học
-- chỉnh lại l.userid = 4 và l.courseid = 4 nếu cần lấy cho user và khóa học khác
-- chỉnh lại l.target nếu cần lấy log cho loại hoạt động khác
-- vd: 'course_module', 'question', 'lesson', 'resource', 'page'
-- chỉnh lại LIMIT nếu cần lấy nhiều hơn 200 bản ghi
-- Chú ý: 'course_module' là loại hoạt động chung cho tất cả các mô-đun trong khóa học
-- 'question' là hoạt động liên quan đến câu hỏi (quiz)
-- 'lesson' là hoạt động liên quan đến bài học
-- 'resource' là hoạt động liên quan đến tài nguyên (vd: file, link)
-- 'page' là hoạt động liên quan đến trang nội dung
-- Nếu cần lấy log cho các hoạt động khác, có thể thêm vào mảng l.target
-- Ví dụ: 'forum', 'assignment', 'quiz', ...
SELECT
  l.id,
  l.userid AS user_id,
  FROM_UNIXTIME(l.timecreated) AS timestamp,
  l.objecttable,
  l.objectid,
  l.target AS activity_type,
  l.action,
  l.contextinstanceid,
  l.courseid
FROM
  mdl_logstore_standard_log l
WHERE
  l.userid = 4
  AND l.courseid = 4 -- nếu bạn biết trước khóa học
  AND l.target IN ('course_module', 'question', 'lesson', 'resource', 'page')
ORDER BY
  l.timecreated DESC
LIMIT 200





-- LẤY log của user cụ thể trong 1 khoá học có kèm theo cái tag là dok nào với cái bài tập (lesson)
SELECT 
  l.id AS log_id,
  l.userid AS user_id,
  FROM_UNIXTIME(l.timecreated) AS timestamp,
  l.objecttable,
  l.objectid,
  l.target AS activity_type,
  l.action,
  l.contextinstanceid,
  l.courseid,
  t.name AS dok_tag -- đây là DOK level gắn trong tag
FROM
  mdl_logstore_standard_log l
LEFT JOIN mdl_modules m ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target IN ('lesson')
ORDER BY
  l.timecreated DESC
LIMIT 200;





-- thời gian hoàn thành của 1 bài tập (import câu hỏi ở dạng trong 1 lesson)
-- chỉnh lại l.userid = 4 và l.courseid = 4 nếu cần lấy cho user và khóa học khác
SELECT
  l.userid AS user_id,
  l.objectid AS lesson_id,
  MIN(l.timecreated) AS start_time,
  MAX(l.timecreated) AS end_time,
  FROM_UNIXTIME(MIN(l.timecreated)) AS start_time_str,
  FROM_UNIXTIME(MAX(l.timecreated)) AS end_time_str,
  SEC_TO_TIME(MAX(l.timecreated) - MIN(l.timecreated)) AS duration,
  t.name AS dok_tag
FROM mdl_logstore_standard_log l
LEFT JOIN mdl_modules m 
    ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target = 'lesson'
  AND l.action IN ('started', 'ended')
GROUP BY
  l.userid, l.objectid, t.name
ORDER BY
  end_time DESC
LIMIT 200;






-- thời gian hoàn thành của 1 bài tập có kèm theo thông tin khoá học, bài học nào (import câu hỏi ở dạng trong 1 lesson)
-- chỉnh lại l.userid = 4 và l.courseid = 4 nếu cần lấy cho user và khóa học khác
SELECT
  l.userid AS user_id,
  l.objectid AS lesson_id,
  c.fullname AS course_name,
  cs.section AS section_number,
  cs.name AS section_name,
  m.name AS module_name,
  FROM_UNIXTIME(MIN(l.timecreated)) AS start_time,
  FROM_UNIXTIME(MAX(l.timecreated)) AS end_time,
  SEC_TO_TIME(MAX(l.timecreated) - MIN(l.timecreated)) AS duration,
  t.name AS dok_tag
FROM mdl_logstore_standard_log l
LEFT JOIN mdl_modules m 
    ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_course c 
    ON c.id = l.courseid
LEFT JOIN mdl_course_sections cs 
    ON cs.id = cm.section
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target = 'lesson'
  AND l.action IN ('started', 'ended')
GROUP BY
  l.userid, l.objectid, c.fullname, cs.section, cs.name, m.name, t.name
ORDER BY
  MAX(l.timecreated) DESC
LIMIT 200;





-- thời gian hoàn thành của 1 bài tập có kèm theo thông tin khoá học, bài học nào (import câu hỏi ở dạng trong 1 lesson), có kèm theo điểm số
-- chỉnh lại l.userid = 4 và l.courseid = 4 nếu cần lấy cho user và khóa học khác
SELECT
  l.userid AS user_id,
  l.objectid AS lesson_id,
  c.fullname AS course_name,
  cs.section AS section_number,
  cs.name AS section_name,
  m.name AS module_name,
  FROM_UNIXTIME(MIN(l.timecreated)) AS start_time,
  FROM_UNIXTIME(MAX(l.timecreated)) AS end_time,
  SEC_TO_TIME(MAX(l.timecreated) - MIN(l.timecreated)) AS duration,
  t.name AS dok_tag,
  lg.grade AS score
FROM mdl_logstore_standard_log l
LEFT JOIN mdl_modules m 
    ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_course c 
    ON c.id = l.courseid
LEFT JOIN mdl_course_sections cs 
    ON cs.id = cm.section
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
LEFT JOIN mdl_lesson_grades lg
    ON lg.lessonid = l.objectid AND lg.userid = l.userid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target = 'lesson'
  AND l.action IN ('started', 'ended')
GROUP BY
  l.userid, l.objectid, c.fullname, cs.section, cs.name, m.name, t.name, lg.grade
ORDER BY
  MAX(l.timecreated) DESC
LIMIT 200;






-- LẤY log của user cụ thể trong 1 khoá học có kèm theo cái tag là dok nào
-- chỉnh lại l.userid = 4 và l.courseid = 4 nếu cần lấy cho user và khóa học khác
-- chỉnh lại l.target nếu cần lấy log cho loại hoạt động khác
-- vd: 'course_module', 'question', 'lesson', 'resource', 'page'
-- chỉnh lại LIMIT nếu cần lấy nhiều hơn 200 bản ghi
-- Chú ý: 'course_module' là loại hoạt động chung cho tất cả các mô-đun trong khóa học
-- 'question' là hoạt động liên quan đến câu hỏi (quiz)
-- 'lesson' là hoạt động liên quan đến bài học
-- note: 'nếu trong lesson là import câu hỏi thì câu hỏi là lesson'
-- 'resource' là hoạt động liên quan đến tài nguyên (vd: file, link)
-- 'page' là hoạt động liên quan đến trang nội dung
-- Nếu cần lấy log cho các hoạt động khác, có thể thêm vào mảng l.target
-- Ví dụ: 'forum', 'assignment', 'quiz', ...
-- Lưu ý: Cần có bảng mdl_tag_instance để liên kết tag với các mô-đun
-- Cần có bảng mdl_tag để lấy tên tag
-- Cần có bảng mdl_modules để lấy tên mô-đun từ objecttable
-- Cần có bảng mdl_course_modules để lấy thông tin mô-đun cụ thể
SELECT 
  l.id AS log_id,
  l.userid AS user_id,
  FROM_UNIXTIME(l.timecreated) AS timestamp,
  l.objecttable,
  l.objectid,
  l.target AS activity_type,
  l.action,
  l.contextinstanceid,
  l.courseid,
  t.name AS dok_tag -- đây là DOK level gắn trong tag
FROM
  mdl_logstore_standard_log l
LEFT JOIN mdl_modules m ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target IN ('course_module', 'question', 'lesson', 'resource', 'page')
ORDER BY
  l.timecreated DESC
LIMIT 200;




-- chua lam xong, lam xong, attempt 1.0
SELECT
  l.userid AS user_id,
  l.objectid AS lesson_id,
  c.fullname AS course_name,
  cs.section AS section_number,
  cs.name AS section_name,
  m.name AS module_name,
  FROM_UNIXTIME(MIN(l.timecreated)) AS start_time,
  FROM_UNIXTIME(MAX(l.timecreated)) AS end_time,
  SEC_TO_TIME(MAX(l.timecreated) - MIN(l.timecreated)) AS duration,
  t.name AS dok_tag,
  lg.grade AS score,
  COUNT(CASE WHEN l.action = 'started' THEN 1 END) AS started_count,
  COUNT(CASE WHEN l.action = 'ended' THEN 1 END) AS ended_count,
  COUNT(DISTINCT lt.id) AS attempts,
  CASE 
    WHEN COUNT(CASE WHEN l.action = 'ended' THEN 1 END) = 0 THEN 'incomplete'
    WHEN lg.grade IS NOT NULL THEN 'completed'
    ELSE 'in_progress'
  END AS status
FROM mdl_logstore_standard_log l
LEFT JOIN mdl_modules m 
    ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_course c 
    ON c.id = l.courseid
LEFT JOIN mdl_course_sections cs 
    ON cs.id = cm.section
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
LEFT JOIN mdl_lesson_grades lg
    ON lg.lessonid = l.objectid AND lg.userid = l.userid
LEFT JOIN mdl_lesson_timer lt
    ON lt.lessonid = l.objectid AND lt.userid = l.userid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target = 'lesson'
  AND l.action IN ('started', 'ended')
GROUP BY
  l.userid, l.objectid, c.fullname, cs.section, cs.name, m.name, t.name, lg.grade
ORDER BY
  MAX(l.timecreated) DESC
LIMIT 200;






-- đếm số điểm hiện tại của bài tập - không cần hoàn thành mới tính điểm - 1.1
SELECT 
  u.id AS user_id,
  u.firstname,
  u.lastname,
  l.id AS lesson_id,
  l.name AS lesson_name,

  -- Điểm thật nếu đã hoàn thành
  lg.grade AS real_grade,

  -- Tính tổng số câu đúng hiện tại (la.correct = 1)
  CASE 
    WHEN lg.grade IS NULL AND total_questions > 0 THEN 
      ROUND(100.0 * correct_answers / total_questions, 2)
    ELSE NULL
  END AS estimated_grade,

  -- Ghi chú xem là điểm thật hay tạm
  CASE 
    WHEN lg.grade IS NOT NULL THEN 'Real'
    ELSE 'Estimated'
  END AS grade_type

FROM mdl_user u
JOIN mdl_lesson l
-- Điểm thật
LEFT JOIN mdl_lesson_grades lg ON lg.lessonid = l.id AND lg.userid = u.id

-- Tổng số câu đúng
LEFT JOIN (
  SELECT lessonid, userid, COUNT(*) AS correct_answers
  FROM mdl_lesson_attempts
  WHERE correct = 1
  GROUP BY lessonid, userid
) corrects ON corrects.lessonid = l.id AND corrects.userid = u.id

-- Tổng số câu trong bài học
LEFT JOIN (
  SELECT lessonid, COUNT(*) AS total_questions
  FROM mdl_lesson_pages
  WHERE qtype > 0  -- chỉ đếm câu hỏi, loại qtype = 0 là thông tin
  GROUP BY lessonid
) questions ON questions.lessonid = l.id

WHERE u.id = 4
GROUP BY u.id, l.id, lg.grade, correct_answers, total_questions;





-- chua lam xong, lam xong, attempt - 1.2
SELECT
  l.userid AS user_id,
  l.objectid AS lesson_id,
  c.fullname AS course_name,
  cs.section AS section_number,
  cs.name AS section_name,
  m.name AS module_name,
  FROM_UNIXTIME(MIN(l.timecreated)) AS start_time,
  FROM_UNIXTIME(MAX(l.timecreated)) AS end_time,
  SEC_TO_TIME(MAX(l.timecreated) - MIN(l.timecreated)) AS duration,
  t.name AS dok_tag,
  lg.grade AS score,
  COUNT(CASE WHEN l.action = 'started' THEN 1 END) AS started_count,
  COUNT(CASE WHEN l.action = 'ended' THEN 1 END) AS ended_count,
  COUNT(DISTINCT lt.id) AS attempts,
  CASE 
    WHEN COUNT(CASE WHEN l.action = 'ended' THEN 1 END) = 0 THEN 'incomplete'
    WHEN lg.grade IS NOT NULL THEN 'completed'
    ELSE 'in_progress'
  END AS status
FROM mdl_logstore_standard_log l
LEFT JOIN mdl_modules m 
    ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm 
    ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_course c 
    ON c.id = l.courseid
LEFT JOIN mdl_course_sections cs 
    ON cs.id = cm.section
LEFT JOIN mdl_tag_instance ti 
    ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t 
    ON t.id = ti.tagid
LEFT JOIN mdl_lesson_grades lg
    ON lg.lessonid = l.objectid AND lg.userid = l.userid
LEFT JOIN mdl_lesson_timer lt
    ON lt.lessonid = l.objectid AND lt.userid = l.userid
WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target = 'lesson'
  AND l.action IN ('started', 'ended')
GROUP BY
  l.userid, l.objectid, c.fullname, cs.section, cs.name, m.name, t.name, lg.grade
ORDER BY
  MAX(l.timecreated) DESC
LIMIT 200;





-- đếm số điểm hiện tại của bài tập - không cần hoàn thành mới tính điểm - 1.1 + 1.2
SELECT 
  u.id AS user_id,
  u.firstname,
  u.lastname,
  l.id AS lesson_id,
  l.name AS lesson_name,

  -- Điểm thật nếu đã hoàn thành
  lg.grade AS real_grade,

  -- Tính tổng số câu đúng hiện tại (la.correct = 1)
  CASE 
    WHEN lg.grade IS NULL AND total_questions > 0 THEN 
      ROUND(100.0 * correct_answers / total_questions, 2)
    ELSE NULL
  END AS estimated_grade,

  -- Ghi chú xem là điểm thật hay tạm
  CASE 
    WHEN lg.grade IS NOT NULL THEN 'Real'
    ELSE 'Estimated'
  END AS grade_type

FROM mdl_user u
JOIN mdl_lesson l
-- Điểm thật
LEFT JOIN mdl_lesson_grades lg ON lg.lessonid = l.id AND lg.userid = u.id

-- Tổng số câu đúng
LEFT JOIN (
  SELECT lessonid, userid, COUNT(*) AS correct_answers
  FROM mdl_lesson_attempts
  WHERE correct = 1
  GROUP BY lessonid, userid
) corrects ON corrects.lessonid = l.id AND corrects.userid = u.id

-- Tổng số câu trong bài học
LEFT JOIN (
  SELECT lessonid, COUNT(*) AS total_questions
  FROM mdl_lesson_pages
  WHERE qtype > 0  -- chỉ đếm câu hỏi, loại qtype = 0 là thông tin
  GROUP BY lessonid
) questions ON questions.lessonid = l.id

WHERE u.id = 4
GROUP BY u.id, l.id, lg.grade, correct_answers, total_questions;





-- LẤY log bài tập của user cụ thể trong 1 khoá học có kèm theo thông tin bài học, khoá học, section, mô-đun, tag dok, thời gian bắt đầu và kết thúc, thời gian hoàn thành, điểm số
-- chỉnh lại l.userid = 4 và l.courseid = 4 nếu cần lấy cho user và khóa học khác
-- chỉnh lại l.target nếu cần lấy log cho loại hoạt động khác
-- Gộp 1.0 và 1.1 và 1.2
-- Có 1 trường hợp chưa hoạt động đúng là khi bài tập chưa hoàn thành thì nó hiện duration = 00:00:00
-- Đúng phải là thời gian đã làm là bao lâu
-- Các trường khác đã đủ đối với log là bài tập để train model
-- Hiện tại thiếu video

SELECT
  u.id AS user_id,
  u.firstname,
  u.lastname,
  l.objectid AS lesson_id,
  ls.name AS lesson_name,
  c.fullname AS course_name,
  cs.section AS section_number,
  cs.name AS section_name,
  m.name AS module_name,
  FROM_UNIXTIME(MIN(l.timecreated)) AS start_time,
  FROM_UNIXTIME(MAX(l.timecreated)) AS end_time,
  SEC_TO_TIME(MAX(l.timecreated) - MIN(l.timecreated)) AS duration,
  t.name AS dok_tag,

  -- Điểm: thực hoặc tạm tính
  CASE 
    WHEN lg.grade IS NOT NULL THEN lg.grade
    WHEN corrects.correct_answers IS NOT NULL AND questions.total_questions > 0 THEN 
      ROUND(100.0 * corrects.correct_answers / questions.total_questions, 2)
    ELSE NULL
  END AS score,

  -- Ghi chú điểm là thật hay tạm
  CASE 
    WHEN lg.grade IS NOT NULL THEN 'Real'
    WHEN corrects.correct_answers IS NOT NULL THEN 'Estimated'
    ELSE 'No attempts'
  END AS grade_type

FROM mdl_logstore_standard_log l

JOIN mdl_user u ON u.id = l.userid
LEFT JOIN mdl_lesson ls ON ls.id = l.objectid
LEFT JOIN mdl_modules m ON m.name = l.objecttable
LEFT JOIN mdl_course_modules cm ON cm.module = m.id AND cm.instance = l.objectid
LEFT JOIN mdl_course c ON c.id = l.courseid
LEFT JOIN mdl_course_sections cs ON cs.id = cm.section
LEFT JOIN mdl_tag_instance ti ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
LEFT JOIN mdl_tag t ON t.id = ti.tagid

-- Điểm thực
LEFT JOIN mdl_lesson_grades lg ON lg.lessonid = l.objectid AND lg.userid = l.userid

-- Câu trả lời đúng
LEFT JOIN (
  SELECT lessonid, userid, COUNT(*) AS correct_answers
  FROM mdl_lesson_attempts
  WHERE correct = 1
  GROUP BY lessonid, userid
) corrects ON corrects.lessonid = l.objectid AND corrects.userid = l.userid

-- Tổng số câu hỏi trong lesson
LEFT JOIN (
  SELECT lessonid, COUNT(*) AS total_questions
  FROM mdl_lesson_pages
  WHERE qtype > 0
  GROUP BY lessonid
) questions ON questions.lessonid = l.objectid

WHERE
  l.userid = 4
  AND l.courseid = 4
  AND l.target = 'lesson'
  AND l.action IN ('started', 'ended')

GROUP BY
  u.id, u.firstname, u.lastname, l.objectid, ls.name,
  c.fullname, cs.section, cs.name, m.name, t.name,
  lg.grade, corrects.correct_answers, questions.total_questions

ORDER BY
  MAX(l.timecreated) DESC
LIMIT 200;


----------- KẾT THÚC -----------