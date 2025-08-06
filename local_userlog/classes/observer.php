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

        // Lấy course_module.id từ event context
        $cmid = $event->contextinstanceid;

        // Lấy sectionid từ bảng course_modules
        $sectionid = $DB->get_field('course_modules', 'section', ['id' => $cmid]);

        // Tạo thư mục lưu log nếu chưa có
        $logdir = $CFG->dataroot . '/local_userlog_data';
        if (!is_dir($logdir)) {
            mkdir($logdir, 0777, true);
        }

        // ==== Log DEBUG riêng ====
        $debuglog = $logdir . '/debug.txt';
        $debugLine = "[DEBUG] time: {$time}, userid: {$userid}, courseid: {$courseid}, sectionid: {$sectionid}, type: {$type}, cmid: {$cmid}\n";
        file_put_contents($debuglog, $debugLine, FILE_APPEND | LOCK_EX);

        // ==== Ghi CSV chính ====
        $path = $logdir . '/user_log_summary.csv';
        if (!file_exists($path)) {
            $header = 'userid,courseid,sectionid,type,time' . "\n";
            file_put_contents($path, $header, FILE_APPEND | LOCK_EX);
        }

        $line = implode(',', [
            $userid,
            $courseid,
            $sectionid,
            $type,
            $time
        ]);
        file_put_contents($path, $line . "\n", FILE_APPEND | LOCK_EX);

        return true;
    }
}