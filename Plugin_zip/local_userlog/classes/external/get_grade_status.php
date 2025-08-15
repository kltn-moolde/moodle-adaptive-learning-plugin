<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_grade_status extends external_api {
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
            SELECT gi.itemname, gg.finalgrade, gi.gradepass,
                   CASE WHEN gg.finalgrade >= gi.gradepass THEN 'Pass' ELSE 'Fail' END AS status
            FROM {grade_grades} gg
            JOIN {grade_items} gi ON gg.itemid = gi.id
            WHERE gg.userid = :userid AND gi.courseid = :courseid
        ";

        $records = $DB->get_records_sql($sql, ['userid' => $userid, 'courseid' => $courseid]);

        $result = [];
        foreach ($records as $r) {
            $result[] = [
                'itemname' => $r->itemname,
                'finalgrade' => round((float)$r->finalgrade, 2),
                'gradepass' => round((float)$r->gradepass, 2),
                'status' => $r->status
            ];
        }

        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'itemname' => new external_value(PARAM_TEXT),
                'finalgrade' => new external_value(PARAM_FLOAT),
                'gradepass' => new external_value(PARAM_FLOAT),
                'status' => new external_value(PARAM_TEXT)
            ])
        );
    }
}