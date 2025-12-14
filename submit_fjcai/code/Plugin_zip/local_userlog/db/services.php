<?php

$functions = [
   'local_userlog_import_questions_from_xml' => [
        'classname'   => 'local_userlog\external\import_questions_from_xml',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/import_questions_from_xml.php',
        'description' => 'Import questions from XML into a category',
        'type'        => 'write',
        'ajax'        => true,
        'capabilities'=> '',
    ],
    'local_userlog_get_logs' => [
        'classname'   => 'local_userlog\external\get_user_logs',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_user_logs.php',
        'description' => 'Get recent logs by user id',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/logstore:read',
    ],
    'local_userlog_get_logs_course' => [
        'classname'   => 'local_userlog\external\get_user_logs_course',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_user_logs_course.php',
        'description' => 'Get recent logs by course id',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/logstore:read',
    ],
    'local_userlog_get_module_logs' => [
        'classname'   => 'local_userlog\external\get_module_logs',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_module_logs.php',
        'description' => 'Get logs for specific module (cmid)',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/logstore:read',
    ],
    'local_userlog_get_access_count' => [
        'classname'   => 'local_userlog\external\get_access_count',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_access_count.php',
        'description' => 'Get access count of activity types by user',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/logstore:read',
    ],
    'local_userlog_get_completion_rate' => [
        'classname'   => 'local_userlog\external\get_completion_rate',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_completion_rate.php',
        'description' => 'Get course completion rate of a user',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/course:isincompletionreports',
    ],
    'local_userlog_get_time_diffs' => [
        'classname'   => 'local_userlog\external\get_time_diffs',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_time_diffs.php',
        'description' => 'Get time difference between log entries',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/logstore:read',
    ],
    'local_userlog_get_quiz_attempts' => [ // ok
        'classname'   => 'local_userlog\external\get_quiz_attempts',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_quiz_attempts.php',
        'description' => 'Get number of quiz attempts by user',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_total_quiz_time' => [ // ok
        'classname'   => 'local_userlog\external\get_total_quiz_time',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_total_quiz_time.php',
        'description' => 'Get total quiz time (in seconds) for a user in a course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_resource_views' => [ // ok
        'classname'   => 'local_userlog\external\get_resource_views',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_resource_views.php',
        'description' => 'Get number of resource views (dynamic types) for a user in a course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_learning_days' => [ // ok
        'classname'   => 'local_userlog\external\get_learning_days',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_learning_days.php',
        'description' => 'Get number of learning days for a user in a course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_pass_quiz_count' => [ // ok
        'classname'   => 'local_userlog\external\get_pass_quiz_count',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_pass_quiz_count.php',
        'description' => 'Get number of passed quiz attempts by user in a course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_pass_quiz_count_attempt' => [ // ok
        'classname'   => 'local_userlog\external\get_pass_quiz_count_attempt',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_pass_quiz_count_attempt.php',
        'description' => 'Get number of passed quiz attempts by user in a course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_avg_quiz_score' => [ //ok
        'classname'   => 'local_userlog\external\get_avg_quiz_score',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_avg_quiz_score.php',
        'description' => 'Tính điểm trung bình của các bài quiz đã hoàn thành',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_total_resources_by_section' => [ // ok
        'classname'   => 'local_userlog\external\get_total_resources_by_section',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_total_resources_by_section.php',
        'description' => 'Get total number of resources (resource, hvp) in a section',
        'type'        => 'read',
        'ajax'        => true
    ],
    'local_userlog_get_viewed_resources_distinct_by_section' => [ // ok
        'classname'   => 'local_userlog\external\get_viewed_resources_distinct_by_section',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_viewed_resources_distinct_by_section.php',
        'description' => 'Get number of distinct resources viewed by a user in a section',
        'type'        => 'read',
        'ajax'        => true
    ],
    'local_userlog_get_latest_quiz_pass_status_by_section' => [ // ok
        'classname'   => 'local_userlog\external\get_latest_quiz_pass_status_by_section',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_latest_quiz_pass_status_by_section.php',
        'description' => 'Get latest quiz pass status by user in a section',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_category_questionbank' => [ // ok
        'classname'   => 'local_userlog\external\get_category_questionbank',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_category_questionbank.php',
        'description' => 'Get question bank categories (hierarchical) for a given course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_create_quiz_from_categories' => [ // ok
        'classname'   => 'local_userlog\external\create_quiz_from_categories',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/create_quiz_from_categories.php',
        'description' => 'Create a quiz in a given course from selected question bank categories, with specific numbers of easy, medium, and hard questions',
        'type'        => 'write',
        'ajax'        => true,
    ],
    'local_userlog_get_quiz_tags' => [ // ok
        'classname'   => 'local_userlog\external\get_quiz_tags',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_quiz_tags.php',
        'description' => 'Get tags of a quiz by quiz ID',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities' => 'moodle/course:view',
    ],
    'local_userlog_get_user_section_avg_grade' => [ // ok
        'classname'   => 'local_userlog\external\get_user_section_avg_grade',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_user_section_avg_grade.php',
        'description' => 'Get average grade of a user in a specific section of a course',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities'=> 'moodle/course:view',
    ],
    'local_userlog_get_section_completion' => [ // ok
        'classname'   => 'local_userlog\external\get_section_completion',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_section_completion.php',
        'description' => 'Get section completion stats (total, completed, rate) for a user',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_grade_course' => [ // ok
        'classname'   => 'local_userlog\external\get_grade_course',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_grade_course.php',
        'description' => 'Get grade information for all users in a course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_quiz_questions' => [ // ok
        'classname'   => 'local_userlog\external\get_quiz_questions',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_quiz_questions.php',
        'description' => 'Get questions of a quiz by quiz ID',
        'type'        => 'read',
        'ajax'        => true,
    ],
    "local_userlog_get_score_section" => [
        'classname'   => 'local_userlog\external\get_score_section',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_score_section.php',
        'description' => 'Get user scores for quizzes in a course, optionally filtered by section',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_grade_status' => [
        'classname'   => 'local_userlog\external\get_grade_status',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_grade_status.php',
        'description' => 'Get grade status (pass/fail) by user',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_total_study_time' => [
        'classname'   => 'local_userlog\external\get_total_study_time',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_total_study_time.php',
        'description' => 'Estimate total time spent on course',
        'type'        => 'read',
        'ajax'        => true,
    ],
    'local_userlog_get_user_object_activity_summary' => [
        'classname' => 'local_userlog\external\get_user_object_activity_summary',
        'methodname' => 'execute',
        'classpath' => 'local/userlog/classes/external/get_user_object_activity_summary.php',
        'description' => 'Lấy danh sách objecttable và objectid hoạt động của user trong khoá học',
        'type' => 'read',
        'capabilities' => ''
    ],
];

$services = [
    'User Log API Service' => [
        'functions' => [
            'local_userlog_import_questions_from_xml',
            'local_userlog_get_logs',  // ok
            'local_userlog_get_logs_course', // ok
            'local_userlog_get_module_logs',    
            'local_userlog_get_access_count', 
            'local_userlog_get_completion_rate',
            'local_userlog_get_time_diffs',
            'local_userlog_get_quiz_attempts', // ok
            'local_userlog_get_total_quiz_time', // ok
            'local_userlog_get_resource_views', // ok
            'local_userlog_get_learning_days', // ok
            'local_userlog_get_pass_quiz_count', // ok
            'local_userlog_get_pass_quiz_count_attempt', // ok
            'local_userlog_get_avg_quiz_score', // ok
            'local_userlog_get_total_resources_by_section', // ok
            'local_userlog_get_viewed_resources_distinct_by_section', // ok
            'local_userlog_get_latest_quiz_pass_status_by_section', // ok
            'local_userlog_get_category_questionbank', // ok
            'local_userlog_create_quiz_from_categories', // ok
            'local_userlog_get_quiz_tags', // ok
            'local_userlog_get_user_section_avg_grade', // ok
            'local_userlog_get_section_completion', // ok
            'local_userlog_get_grade_status',
            'local_userlog_get_grade_course', // ok
            'local_userlog_get_total_study_time',
            'local_userlog_get_user_object_activity_summary',
            'local_userlog_get_quiz_questions',
            'local_userlog_get_score_section'
        ],
        'enabled' => 1,
        'restrictedusers' => 0
    ]
];
