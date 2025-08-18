<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class get_completion_rate extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'    => new external_value(PARAM_INT, 'User ID'),
            'courseid'  => new external_value(PARAM_INT, 'Course ID', VALUE_OPTIONAL)
        ]);
    }

    public static function execute($userid, $courseid = 0) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid'   => $userid,
            'courseid' => $courseid
        ]);

        $params = ['userid' => $userid];
        $sql = "
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN completionstate = 1 THEN 1 ELSE 0 END) AS completed
            FROM {course_modules_completion} cmc
            JOIN {course_modules} cm ON cm.id = cmc.coursemoduleid
        ";

        if ($courseid > 0) {
            $sql .= " WHERE cmc.userid = :userid AND cm.course = :courseid";
            $params['courseid'] = $courseid;
        } else {
            $sql .= " WHERE cmc.userid = :userid";
        }

        $record = $DB->get_record_sql($sql, $params);

        $total = (int)($record->total ?? 0);
        $completed = (int)($record->completed ?? 0);
        $rate = $total > 0 ? round($completed / $total, 4) : 0.0;

        return [
            'userid' => $userid,
            'courseid' => $courseid,
            'completed' => $completed,
            'total' => $total,
            'completion_rate' => $rate
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'userid'           => new external_value(PARAM_INT),
            'courseid'         => new external_value(PARAM_INT),
            'completed'        => new external_value(PARAM_INT),
            'total'            => new external_value(PARAM_INT),
            'completion_rate'  => new external_value(PARAM_FLOAT)
        ]);
    }
}