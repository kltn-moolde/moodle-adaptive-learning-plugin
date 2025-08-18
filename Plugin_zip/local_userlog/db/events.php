<?php

$observers = [
    [
        'eventname'   => '\mod_quiz\event\attempt_submitted',
        'callback'    => '\local_userlog\observer::log_learning_event',
    ],
    [
        'eventname'   => '\mod_quiz\event\course_module_viewed',
        'callback'    => '\local_userlog\observer::log_learning_event',
    ],
    [
        'eventname'   => '\mod_hvp\event\course_module_viewed',
        'callback'    => '\local_userlog\observer::log_learning_event',
    ],
    [
        'eventname'   => '\mod_resource\event\course_module_viewed',
        'callback'    => '\local_userlog\observer::log_learning_event',
    ]
];