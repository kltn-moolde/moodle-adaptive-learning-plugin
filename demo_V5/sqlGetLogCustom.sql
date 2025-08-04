SELECT
    u.id AS user_id,
    u.fullname AS user_name,
    u.email AS user_email,
    c.id AS course_id,
    c.fullname AS course_name,
    l.id AS lesson_id,
    l.name AS lesson_name,
    lcm.timecreated AS completion_time
FROM
    mdl_user u
JOIN
    mdl_course c ON c.id = :courseid
JOIN
    mdl_lesson l ON l.course = c.id
JOIN
    mdl_lesson_completion lcm ON lcm.lessonid = l.id AND lcm.userid = u.id
WHERE
    u.id IN (SELECT userid FROM mdl_role_assignments WHERE contextid = :contextid)
    AND lcm.timecreated >= :starttime
    AND lcm.timecreated <= :endtime
ORDER BY
    u.id, l.id;
