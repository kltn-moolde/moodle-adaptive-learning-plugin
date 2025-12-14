<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_value;
use external_single_structure;

class get_section_completion extends external_api {

    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'   => new external_value(PARAM_INT, 'User ID'),
            'sectionid' => new external_value(PARAM_INT, 'Section ID'),
        ]);
    }

    public static function execute($userid, $sectionid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid' => $userid,
            'sectionid' => $sectionid,
        ]);

        $sql = "
            SELECT 
                cm.section AS section_id,
                :userid1 AS userid,
                COUNT(cm.id) AS total_activities,
                SUM(CASE WHEN cmc.completionstate IN (1,2) THEN 1 ELSE 0 END) AS completed_activities,
                ROUND(
                    (SUM(CASE WHEN cmc.completionstate IN (1,2) THEN 1 ELSE 0 END) * 100.0) / COUNT(cm.id),
                    2
                ) AS completion_rate
            FROM {course_modules} cm
            LEFT JOIN {course_modules_completion} cmc
                ON cmc.coursemoduleid = cm.id
               AND cmc.userid = :userid2
            WHERE cm.section = :sectionid
              AND cm.deletioninprogress = 0
            GROUP BY cm.section
        ";

        $params = [
            'userid1'   => $userid,
            'userid2'   => $userid,
            'sectionid' => $sectionid,
        ];

        $record = $DB->get_record_sql($sql, $params);

        if (!$record) {
            // nếu section không tồn tại hoặc user chưa có completion, trả về mặc định
            $record = (object)[
                'section_id' => $sectionid,
                'userid' => $userid,
                'total_activities' => 0,
                'completed_activities' => 0,
                'completion_rate' => 0,
            ];
        }

        return [
            'section_id' => (int)$record->section_id,
            'userid' => (int)$record->userid,
            'total_activities' => (int)$record->total_activities,
            'completed_activities' => (int)$record->completed_activities,
            'completion_rate' => (float)$record->completion_rate,
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'section_id' => new external_value(PARAM_INT, 'Section ID'),
            'userid' => new external_value(PARAM_INT, 'User ID'),
            'total_activities' => new external_value(PARAM_INT, 'Tổng số hoạt động trong section'),
            'completed_activities' => new external_value(PARAM_INT, 'Số hoạt động đã hoàn thành'),
            'completion_rate' => new external_value(PARAM_FLOAT, 'Tỉ lệ hoàn thành (%)'),
        ]);
    }
}