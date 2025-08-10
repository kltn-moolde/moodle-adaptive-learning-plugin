<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_value;
use external_single_structure;

class get_pass_quiz_count_attempt extends external_api {
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
          SELECT COUNT(*) AS pass_attempt_count
            FROM {quiz_attempts} qa
            JOIN {quiz} q 
                ON q.id = qa.quiz
            JOIN {grade_items} gi
                ON gi.iteminstance = q.id AND gi.itemmodule = 'quiz'
            WHERE q.course = :courseid
            AND qa.userid = :userid
            AND qa.state = 'finished'
            AND ROUND((qa.sumgrades / q.sumgrades) * gi.grademax, 2) >= gi.gradepass
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