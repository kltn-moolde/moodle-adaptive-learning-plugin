<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_total_study_time extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User ID'),
            'courseid' => new external_value(PARAM_INT, 'Course ID')
        ]);
    }

    public static function execute($userid, $courseid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid' => $userid,
            'courseid' => $courseid
        ]);

        $sql = "
            SELECT timecreated,
                   timecreated - LAG(timecreated) OVER (PARTITION BY userid ORDER BY timecreated) AS diff
            FROM {logstore_standard_log}
            WHERE userid = :userid AND courseid = :courseid
            ORDER BY timecreated
        ";
        $records = $DB->get_records_sql($sql, ['userid' => $userid, 'courseid' => $courseid]);

        $total = 0;
        foreach ($records as $r) {
            $gap = (int)($r->diff ?? 0);
            if ($gap > 0 && $gap < 1800) { // bỏ qua khoảng cách > 30 phút
                $total += $gap;
            }
        }

        return [
            'userid' => $userid,
            'courseid' => $courseid,
            'total_time_spent' => $total
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'userid' => new external_value(PARAM_INT),
            'courseid' => new external_value(PARAM_INT),
            'total_time_spent' => new external_value(PARAM_INT)
        ]);
    }
}