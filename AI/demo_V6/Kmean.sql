--Đặc trưng mới                     -- Công thức                                 -- Ý nghĩa
-- avg_time_per_quiz                -- time_spent / quiz_attempts.               -- Trung bình 1 quiz học bao lâu
-- avg_resource_views_per_day       -- resource_views / num_learning_days        -- Mỗi ngày xem bao nhiêu tài liệu
-- quiz_success_rate                -- pass_quiz_count / quiz_attempts           -- Tỷ lệ làm quiz đạt
-- avg_quiz_score                   -- avg_quiz_score                            -- Điểm trung bình của các lần làm quiz
-- resource_vs_quiz_ratio           -- resource_views / quiz_attempts            -- Tỷ lệ giữa số lần xem tài liệu và số lần làm quiz



-- Giải --
-- 1. avg_time_per_quiz 
-- Tính số lần làm quiz
SELECT 
    COUNT(*) AS quiz_attempts
FROM mdl_quiz_attempts qa
JOIN mdl_quiz q ON qa.quiz = q.id
WHERE qa.userid = 4 AND q.course = 5;

-- Tính tổng thời gian làm quiz
SELECT SUM(qa.timefinish - qa.timestart) AS total_quiz_time
FROM mdl_quiz_attempts qa
JOIN mdl_quiz q ON qa.quiz = q.id
WHERE qa.userid = 4 AND q.course = 5
  AND qa.timefinish > 0;


-- 2. avg_resource_views_per_day 
-- Tính số lần xem tài liệu là LO
-- resource_views
SELECT COUNT(*) AS resource_views
FROM mdl_logstore_standard_log l
WHERE l.userid = 4
  AND l.courseid = 5
  AND l.objecttable IN ('resource', 'hvp', 'quiz')
  AND l.action = 'viewed';
  
-- Tính số ngày học có hoạt động học tập
-- num_learning_days
SELECT COUNT(DISTINCT FROM_UNIXTIME(l.timecreated, '%Y-%m-%d')) AS num_learning_days
FROM mdl_logstore_standard_log l
WHERE l.userid = 4
  AND l.courseid = 5
  AND l.objecttable IN ('resource', 'quiz', 'hvp') -- hoặc tùy các hoạt động bạn định nghĩa là "học"
  AND l.action = 'viewed'; 



-- 3. quiz_success_rate
-- Tính số lần làm quiz pass
-- pass_quiz_count
SELECT COUNT(*) AS pass_quiz_count
FROM mdl_quiz_attempts qa
JOIN mdl_quiz q ON qa.quiz = q.id
JOIN mdl_grade_items gi ON gi.iteminstance = q.id AND gi.itemmodule = 'quiz'
WHERE qa.userid = 4
  AND q.course = 5
  AND qa.state = 'finished'
  AND qa.sumgrades >= gi.gradepass;

-- 4. avg_quiz_score
-- Tính điểm trung bình của các lần làm quiz
  SELECT
    ROUND(AVG(qa.sumgrades), 2) AS avg_quiz_score
FROM mdl_quiz_attempts qa
JOIN mdl_quiz q ON qa.quiz = q.id
WHERE qa.userid = 4
  AND q.course = 5
  AND qa.state = 'finished'
  AND qa.sumgrades IS NOT NULL;  

-- 5. resource_vs_quiz_ratio
-- Tính tỷ lệ giữa số lần xem tài liệu và số lần làm quiz
SELECT COUNT(*) AS resource_views
FROM mdl_logstore_standard_log l
WHERE l.userid = 4
  AND l.courseid = 5
  AND l.objecttable IN ('resource', 'hvp')
  AND l.action = 'viewed';  

SELECT 
    COUNT(*) AS quiz_attempts
FROM mdl_quiz_attempts qa
JOIN mdl_quiz q ON qa.quiz = q.id
WHERE qa.userid = 4 AND q.course = 5;  