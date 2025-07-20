SELECT * FROM moodle.mdl_tag_instance;
show create table mdl_tag_instance
SELECT * FROM moodle.mdl_course_modules;
SELECT * FROM moodle.mdl_lesson;
SELECT * FROM moodle.mdl_modules

-- LẤY TAG DOK của từng LO cụ thể trong 1 khoá học    
SELECT 
    t.name AS tag_name,
    l.*
FROM 
    mdl_tag_instance ti
JOIN 
    mdl_tag t ON t.id = ti.tagid
JOIN 
    mdl_course_modules cm ON cm.id = ti.itemid
JOIN 
    mdl_modules m ON m.id = cm.module
JOIN 
    mdl_lesson l ON l.id = cm.instance
WHERE 
    ti.itemtype = 'course_modules' and l.course = 3
 
   
-- LẤY log của user cụ thể
SELECT *
            FROM mdl_logstore_standard_log l
            WHERE l.userid = 4
            ORDER BY l.timecreated DESC   

-- LẤY log của user cụ thể trong 1 khoá học
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
  AND l.courseid = 3 -- nếu bạn biết trước khóa học
  AND l.target IN ('course_module', 'question', 'lesson', 'resource', 'page')
ORDER BY
  l.timecreated DESC
LIMIT 200


-- LẤY log của user cụ thể trong 1 khoá học có kèm theo cái tag là dok nào
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
  AND l.courseid = 3
  AND l.target IN ('course_module', 'question', 'lesson', 'resource', 'page')
ORDER BY
  l.timecreated DESC
LIMIT 200;


SELECT * FROM mdl_resource WHERE id = 3;
SELECT * FROM mdl_lesson_pages WHERE id = 5;





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