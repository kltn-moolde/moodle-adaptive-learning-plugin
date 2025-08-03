<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_quiz_attempts extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User ID')
        ]);
    }

    public static function execute($userid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), ['userid' => $userid]);

        $sql = "
            SELECT quiz, COUNT(*) as num_attempts
            FROM {quiz_attempts}
            WHERE userid = :userid
            GROUP BY quiz
        ";
        $records = $DB->get_records_sql($sql, ['userid' => $userid]);

        $result = [];
        foreach ($records as $record) {
            $result[] = [
                'quizid' => $record->quiz,
                'num_attempts' => (int)$record->num_attempts
            ];
        }
        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'quizid' => new external_value(PARAM_INT),
                'num_attempts' => new external_value(PARAM_INT)
            ])
        );
    }
}