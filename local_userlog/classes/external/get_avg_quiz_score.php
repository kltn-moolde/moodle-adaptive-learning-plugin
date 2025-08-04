<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_value;
use external_single_structure;

class get_avg_quiz_score extends external_api {
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
            SELECT ROUND(AVG(qa.sumgrades), 2) AS avg_quiz_score
            FROM {quiz_attempts} qa
            JOIN {quiz} q ON qa.quiz = q.id
            WHERE qa.userid = :userid
              AND q.course = :courseid
              AND qa.state = 'finished'
              AND qa.sumgrades IS NOT NULL
        ";

        $params = ['userid' => $userid, 'courseid' => $courseid];
        $score = $DB->get_field_sql($sql, $params);

        return [
            'avg_quiz_score' => (float)$score
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'avg_quiz_score' => new external_value(PARAM_FLOAT, 'Trung bình điểm các bài quiz')
        ]);
    }
}