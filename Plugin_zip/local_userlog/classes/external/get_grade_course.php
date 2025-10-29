<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_grade_course extends external_api {

    /**
     * Định nghĩa tham số đầu vào cho API
     */
    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
        ]);
    }

    /**
     * Thực thi hàm chính
     */
    public static function execute($courseid) {
        global $DB;

        // Xác thực tham số
        self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid
        ]);

        // Câu SQL lấy danh sách điểm của tất cả user trong 1 course
        $sql = "
            SELECT 
                gg.id,
                gg.timemodified,
                u.id AS user_id,
                gi.courseid,
                gi.itemname AS grade_item,
                gi.itemtype,
                gg.finalgrade
            FROM {grade_grades} gg
            JOIN {grade_items} gi ON gg.itemid = gi.id
            JOIN {user} u ON gg.userid = u.id
            WHERE gi.courseid = :courseid
            ORDER BY u.lastname, gi.itemname
        ";

        // Lấy danh sách
        $records = $DB->get_records_sql($sql, ['courseid' => $courseid]);

        // Chuyển sang mảng kết quả trả về
        $result = [];
        foreach ($records as $r) {
            $result[] = [
                'id' => (int)$r->id,
                'user_id' => (int)$r->user_id,
                'courseid' => (int)$r->courseid,
                'grade_item' => $r->grade_item,
                'itemtype' => $r->itemtype,
                'finalgrade' => isset($r->finalgrade) ? (float)$r->finalgrade : null,
                'timemodified' => (int)$r->timemodified,
            ];
        }

        return $result;
    }

    /**
     * Định nghĩa cấu trúc dữ liệu trả về
     */
    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'id' => new external_value(PARAM_INT, 'Grade record ID'),
                'user_id' => new external_value(PARAM_INT, 'User ID'),
                'courseid' => new external_value(PARAM_INT, 'Course ID'),
                'grade_item' => new external_value(PARAM_TEXT, 'Tên mục điểm'),
                'itemtype' => new external_value(PARAM_TEXT, 'Loại mục điểm'),
                'finalgrade' => new external_value(PARAM_FLOAT, 'Điểm cuối', VALUE_OPTIONAL),
                'timemodified' => new external_value(PARAM_INT, 'Timestamp cập nhật'),
            ])
        );
    }
}