<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_time_diffs extends external_api {
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
            SELECT id, userid, timecreated,
                   timecreated - LAG(timecreated) OVER (PARTITION BY userid ORDER BY timecreated) AS time_diff
            FROM {logstore_standard_log}
            WHERE userid = :userid AND courseid = :courseid
            ORDER BY timecreated
        ";
        $params = ['userid' => $userid, 'courseid' => $courseid];
        $records = $DB->get_records_sql($sql, $params);

        $result = [];
        foreach ($records as $r) {
            $result[] = [
                'logid' => $r->id,
                'timecreated' => $r->timecreated,
                'time_diff' => (int)($r->time_diff ?? 0)
            ];
        }

        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'logid' => new external_value(PARAM_INT),
                'timecreated' => new external_value(PARAM_INT),
                'time_diff' => new external_value(PARAM_INT)
            ])
        );
    }
}