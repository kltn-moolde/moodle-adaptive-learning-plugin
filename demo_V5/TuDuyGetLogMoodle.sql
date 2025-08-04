
  
SELECT objecttable, objectid, MAX(timecreated) AS latest_time
FROM moodle.mdl_logstore_standard_log 
WHERE userid = 4 
  AND courseid = 5
  AND objecttable IS NOT NULL
GROUP BY objecttable, objectid
ORDER BY latest_time DESC;  
  
-- objecttable,objectid -- Danh sách output
-- course,5
-- resource,6
-- hvp,1
-- quiz,3
-- quiz_attempts,6
-- grade_grades,26
-- course_sections,38
-- course_sections,34
-- course_modules_completion,5
-- course_modules_completion,6
-- course_modules_completion,7
-- quiz_attempts,7
-- course_sections,39-- 


-- Từ bảng course, id = 5
SELECT * FROM mdl_course WHERE id = 5;

-- Từ bảng resource, id = 6
SELECT * FROM mdl_resource WHERE id = 6;

-- Từ bảng hvp (H5P content), id = 1
SELECT * FROM mdl_hvp WHERE id = 1;

-- Từ bảng quiz, id = 3
SELECT * FROM mdl_quiz WHERE id = 3;

-- Từ bảng quiz_attempts, id = 6
SELECT * FROM mdl_quiz_attempts WHERE id = 6;

-- Từ bảng grade_grades, id = 26
SELECT * FROM mdl_grade_grades WHERE id = 26;

-- Từ bảng course_sections, id = 38
SELECT * FROM mdl_course_sections WHERE id = 38;

-- Từ bảng course_sections, id = 34
SELECT * FROM mdl_course_sections WHERE id = 34;

-- Từ bảng course_modules_completion, id = 5
SELECT * FROM mdl_course_modules_completion WHERE id = 5;

-- Từ bảng course_modules_completion, id = 6
SELECT * FROM mdl_course_modules_completion WHERE id = 6;

-- Từ bảng course_modules_completion, id = 7
SELECT * FROM mdl_course_modules_completion WHERE id = 7;

-- Từ bảng quiz_attempts, id = 7
SELECT * FROM mdl_quiz_attempts WHERE id = 7;

-- Từ bảng course_sections, id = 39
SELECT * FROM mdl_course_sections WHERE id = 39;




-- Get log hoàn chỉnh --

-- Đếm số lần truy cập từng loại hoạt động
SELECT 
  userid,
  objecttable,
  COUNT(*) AS num_access
FROM mdl_logstore_standard_log
WHERE userid = 4 AND courseid = 5
  AND action = 'viewed'
  AND objecttable IN ('quiz', 'resource', 'hvp', 'forum')
GROUP BY userid, objecttable;


-- Tính tỷ lệ hoàn thành trên tổng số module của khóa học
SELECT 
  userid,
  COUNT(CASE WHEN completionstate = 1 THEN 1 END) * 1.0 / COUNT(*) AS completion_rate
FROM mdl_course_modules_completion
WHERE userid = 4
GROUP BY userid;


-- Khoảng thời gian giữa các lần học
SELECT 
  userid,
  timecreated,
  FROM_UNIXTIME(timecreated) as readable_time
FROM mdl_logstore_standard_log
WHERE userid = 4 AND courseid = 5
ORDER BY timecreated;


-- Khoảng cách giữa 2 lần học gần nhau (bằng giây)
SELECT 
  userid,
  timecreated,
  timecreated - LAG(timecreated) OVER (PARTITION BY userid ORDER BY timecreated) AS time_diff
FROM mdl_logstore_standard_log
WHERE userid = 4 AND courseid = 5;

--  Số lần làm lại quiz
SELECT 
  userid,
  quiz,
  COUNT(*) AS num_attempts
FROM mdl_quiz_attempts
WHERE userid = 4
GROUP BY userid, quiz;


-- Vượt qua hay chưa vượt qua bài tập (pass/fail)
SELECT 
  gg.userid,
  gi.itemname,
  gg.finalgrade,
  gi.gradepass,
  CASE 
    WHEN gg.finalgrade >= gi.gradepass THEN 'Pass'
    ELSE 'Fail'
  END AS status
FROM mdl_grade_grades gg
JOIN mdl_grade_items gi ON gg.itemid = gi.id
WHERE gg.userid = 4 AND gi.courseid = 5;


-- Thời lượng giả định giữa 2 log liền nhau
SELECT 
  userid,
  timecreated,
  timecreated - LAG(timecreated) OVER (PARTITION BY userid ORDER BY timecreated) AS session_time
FROM mdl_logstore_standard_log
WHERE userid = 4 AND courseid = 5;