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
    ]
];

$services = [
    'User Log API Service' => [
        'functions' => ['local_userlog_get_logs', 'local_userlog_get_module_logs'],
        'enabled' => 1,
        'restrictedusers' => 0
    ]
];
