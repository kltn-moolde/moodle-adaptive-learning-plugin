<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_user_object_activity_summary extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User ID'),
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
        ]);
    }

    public static function execute($userid, $courseid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid' => $userid,
            'courseid' => $courseid
        ]);

        $sql = "
            SELECT objecttable, objectid, MAX(timecreated) AS latest_time
            FROM {logstore_standard_log}
            WHERE userid = :userid
              AND courseid = :courseid
              AND objecttable IS NOT NULL
            GROUP BY objecttable, objectid
            ORDER BY latest_time DESC
        ";

        $params = ['userid' => $userid, 'courseid' => $courseid];
        $records = $DB->get_records_sql($sql, $params);

        $result = [];
        foreach ($records as $r) {
            $result[] = [
                'objecttable' => $r->objecttable,
                'objectid' => $r->objectid,
                'latest_time' => $r->latest_time
            ];
        }

        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'objecttable' => new external_value(PARAM_TEXT),
                'objectid' => new external_value(PARAM_INT),
                'latest_time' => new external_value(PARAM_INT),
            ])
        );
    }
}