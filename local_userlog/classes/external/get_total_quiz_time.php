<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class get_total_quiz_time extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'    => new external_value(PARAM_INT, 'User ID'),
            'courseid'  => new external_value(PARAM_INT, 'Course ID')
        ]);
    }

    public static function execute($userid, $courseid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid'    => $userid,
            'courseid'  => $courseid
        ]);

        $sql = "
            SELECT SUM(qa.timefinish - qa.timestart) AS total_quiz_time
            FROM {quiz_attempts} qa
            JOIN {quiz} q ON qa.quiz = q.id
            WHERE qa.userid = :userid
              AND q.course = :courseid
              AND qa.timefinish > 0
        ";

        $total = $DB->get_field_sql($sql, [
            'userid'    => $userid,
            'courseid'  => $courseid
        ]);

        return [
            'total_quiz_time' => (int)$total
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'total_quiz_time' => new external_value(PARAM_INT, 'Total quiz time in seconds')
        ]);
    }
}