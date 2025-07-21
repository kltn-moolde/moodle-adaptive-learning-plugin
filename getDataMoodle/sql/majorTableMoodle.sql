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

----------- KẾT THÚC -----------








----------- LỖI -----------
-- Truy vấn để lấy tất cả thông tin mình cần nhưng bị lỗi, chưa đúng
WITH log_data AS (
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
    t.name AS dok_tag,
    cm.id AS course_module_id,
    cm.instance,
    cm.module,
    cm.idnumber,
    -- Tách chapter và unit từ idnumber nếu có
    SUBSTRING_INDEX(idnumber, '.', 1) AS chapter,
    SUBSTRING_INDEX(SUBSTRING_INDEX(idnumber, '.', 2), '.', -1) AS unit,
    
    -- Tính time_spent bằng cách lấy hiệu giữa 2 lần truy cập liên tiếp
    TIMESTAMPDIFF(SECOND,
      LAG(FROM_UNIXTIME(l.timecreated)) OVER (PARTITION BY l.userid ORDER BY l.timecreated),
      FROM_UNIXTIME(l.timecreated)
    ) AS time_spent

  FROM mdl_logstore_standard_log l
  LEFT JOIN mdl_modules m ON m.name = l.objecttable
  LEFT JOIN mdl_course_modules cm 
      ON cm.module = m.id AND cm.instance = l.objectid
  LEFT JOIN mdl_tag_instance ti 
      ON ti.itemid = cm.id AND ti.itemtype = 'course_modules'
  LEFT JOIN mdl_tag t 
      ON t.id = ti.tagid
  WHERE
    l.userid = 4
    AND l.courseid = 3
    AND l.target IN ('course_module', 'question', 'lesson', 'resource', 'page', 'quiz')
),

-- Lấy điểm và số lần làm bài nếu là quiz
quiz_data AS (
  SELECT
    qa.userid,
    q.id AS quizid,
    qg.grade AS score,
    COUNT(qa.id) AS attempts
  FROM mdl_quiz q
  LEFT JOIN mdl_quiz_grades qg ON qg.quiz = q.id
  LEFT JOIN mdl_quiz_attempts qa ON qa.quiz = q.id AND qa.userid = 4
  WHERE q.course = 3
  GROUP BY qa.userid, q.id, qg.grade
),

-- Lấy thông tin hoàn thành hoạt động
completion_data AS (
  SELECT 
    userid,
    coursemoduleid,
    completionstate AS completed
  FROM mdl_course_modules_completion
  WHERE userid = 4
)

-- Ghép tất cả lại
SELECT
  l.log_id,
  l.user_id,
  l.timestamp,
  l.objecttable,
  l.objectid,
  l.activity_type,
  l.action,
  l.contextinstanceid,
  l.courseid,
  l.dok_tag,
  l.idnumber,
  l.chapter,
  l.unit,
  l.time_spent,
  
  -- Quiz info
  q.score,
  q.attempts,

  -- Có phải dạng đánh giá không?
  CASE 
    WHEN l.objecttable IN ('quiz', 'lesson') THEN 1
    ELSE 0
  END AS has_assessment,

  -- Trạng thái hoàn thành
  c.completed

FROM log_data l
LEFT JOIN quiz_data q 
  ON q.userid = l.user_id AND l.objecttable = 'quiz' AND q.quizid = l.objectid
LEFT JOIN completion_data c 
  ON c.userid = l.user_id AND c.coursemoduleid = l.course_module_id

ORDER BY l.timestamp DESC
LIMIT 200;