<?php

$observers = array(
    array(
        'eventname'   => '*', // bắt tất cả event
        'callback'    => '\local_userlog\observer::any_event',
        'includefile' => null,
        'internal'    => 1, // chạy async
    ),
);