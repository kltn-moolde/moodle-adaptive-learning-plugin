<?php
namespace local_userlog;

defined('MOODLE_INTERNAL') || die();

class observer {

    public static function log_learning_event(\core\event\base $event) {
        global $DB, $CFG;

        $userid = $event->userid;
        $courseid = $event->courseid;
        $type = $event->objecttable; // quiz, resource, hvp,...
        $time = $event->timecreated;

        // Chỉ log những loại này
        $allowed = ['quiz', 'resource', 'hvp'];
        if (!in_array($type, $allowed)) {
            return true;
        }

        // DEBUG: lưu log test ra file /tmp nếu server hỗ trợ
        @file_put_contents('/tmp/observer_log_debug.txt', "Event: $type - User: $userid\n", FILE_APPEND);

        // Lấy dữ liệu
        $last_result = self::get_last_result($userid, $type);
        $completion = self::get_completion_rate($userid, $courseid);
        $pass = self::get_pass_rate($userid, $courseid);
        $low_score_count = self::get_low_score_quiz_count($userid, $courseid);

        // Tạo thư mục lưu file CSV
        $logdir = $CFG->dataroot . '/local_userlog_data';
        if (!is_dir($logdir)) {
            mkdir($logdir, 0777, true);
        }

        $path = $logdir . '/user_log_summary.csv';

        // Nếu chưa có file => thêm header
        if (!file_exists($path)) {
            $header = 'userid,courseid,last_type,last_result,completion_rate,pass_rate,low_score_quiz_count,time' . "\n";
            file_put_contents($path, $header, FILE_APPEND | LOCK_EX);
        }

        // Ghi log mới
        $line = implode(',', [
            $userid,
            $courseid,
            $type,
            $last_result,
            $completion,
            $pass,
            $low_score_count,
            $time
        ]);
        file_put_contents($path, $line . "\n", FILE_APPEND | LOCK_EX);

        return true;
    }

    private static function get_last_result($userid, $type) {
        // Bạn có thể thay thế bằng logic thật sau này
        return ($type === 'quiz') ? 'fail' : 'done';
    }

    private static function get_completion_rate($userid, $courseid) {
        return 1.0;
    }

    private static function get_pass_rate($userid, $courseid) {
        return 1.0;
    }

    private static function get_low_score_quiz_count($userid, $courseid) {
        return 1;
    }
}