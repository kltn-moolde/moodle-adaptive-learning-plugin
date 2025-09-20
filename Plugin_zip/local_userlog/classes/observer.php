<?php
namespace local_userlog;

defined('MOODLE_INTERNAL') || die();

class observer {

    public static function log_learning_event(\core\event\base $event) {
        global $DB;

        $userid = $event->userid;
        $courseid = $event->courseid;
        $type = $event->objecttable; // quiz, resource, hvp,...
        $objectid = $event->objectid; // ID của resource/quiz
        $time = $event->timecreated;

        // Chỉ log những loại này
        $allowed = ['quiz_attempts', 'resource', 'hvp'];
        if (!in_array($type, $allowed)) {
            return true;
        }

        // Lấy course_module.id từ event context
        $cmid = $event->contextinstanceid;

        // Lấy sectionid từ bảng course_modules
        $sectionid = $DB->get_field('course_modules', 'section', ['id' => $cmid]);

        // ==== Gọi API bên ngoài thay vì ghi file ====
        $payload = [
            'userid' => $userid,
            'courseid' => $courseid,
            'sectionid' => $sectionid,
            'type' => $type,
            'objectid' => $objectid,
            'time' => $time
        ];

        $api_url = 'http://51.68.124.207:8088/api/update-learning-event';

        $options = [
            'http' => [
                'header'  => "Content-Type: application/json\r\n",
                'method'  => 'POST',
                'content' => json_encode($payload),
                'timeout' => 5
            ]
        ];

        $context = stream_context_create($options);
        $result = @file_get_contents($api_url, false, $context);

        if ($result === FALSE) {
            // Ghi lỗi nếu gửi API thất bại
            error_log("❌ Failed to send learning event for user $userid");
        }
        return true;
    }
}