<?php

$functions = [
    'local_userlog_get_logs' => [
        'classname'   => 'local_userlog\external\get_user_logs',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_user_logs.php',
        'description' => 'Get recent logs by user id',
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
    'local_userlog_get_quiz_attempts' => [
        'classname'   => 'local_userlog\external\get_quiz_attempts',
        'methodname'  => 'execute',
        'classpath'   => 'local/userlog/classes/external/get_quiz_attempts.php',
        'description' => 'Get number of quiz attempts by user',
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
    ]
];

$services = [
    'User Log API Service' => [
        'functions' => [
            'local_userlog_get_logs', 
            'local_userlog_get_module_logs', 
            'local_userlog_get_access_count', 
            'local_userlog_get_completion_rate',
            'local_userlog_get_time_diffs',
            'local_userlog_get_quiz_attempts',
            'local_userlog_get_grade_status',
            'local_userlog_get_total_study_time',
            'local_userlog_get_user_object_activity_summary'
        ],
        'enabled' => 1,
        'restrictedusers' => 0
    ]
];
