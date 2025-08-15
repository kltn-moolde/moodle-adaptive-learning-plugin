<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_value;
use external_single_structure;

class get_pass_quiz_count extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'   => new external_value(PARAM_INT, 'User ID'),
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
        ]);
    }

    public static function execute($userid, $courseid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid' => $userid,
            'courseid' => $courseid,
        ]);

        $sql = "
           SELECT COUNT(*) AS pass_quiz_count
            FROM {grade_items} gi
            JOIN {grade_grades} gg 
                ON gi.id = gg.itemid
            JOIN {quiz} q 
                ON q.id = gi.iteminstance 
                AND gi.itemmodule = 'quiz'
            WHERE gi.courseid = :courseid
                AND gg.userid = :userid
                AND gg.rawgrade IS NOT NULL
                AND gg.rawgrade >= gi.gradepass
        ";

        $params = ['userid' => $userid, 'courseid' => $courseid];

        $count = $DB->get_field_sql($sql, $params);

        return [
            'pass_quiz_count' => (int)$count
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'pass_quiz_count' => new external_value(PARAM_INT, 'Số lượng bài quiz vượt qua (pass)')
        ]);
    }
}