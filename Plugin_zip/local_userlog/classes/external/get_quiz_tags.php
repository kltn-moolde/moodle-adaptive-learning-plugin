<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_quiz_tags extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'quizid' => new external_value(PARAM_INT, 'Quiz ID'),
        ]);
    }

    public static function execute($quizid) {
        global $DB;

        // Validate input
        self::validate_parameters(self::execute_parameters(), [
            'quizid' => $quizid
        ]);

        $sql = "
            SELECT q.id,
                   q.name AS quiz_name,
                   t2.name AS tag_name_cm
            FROM {quiz} q
            LEFT JOIN {course_modules} cm
                   ON cm.instance = q.id
                   AND cm.module = (SELECT id FROM {modules} WHERE name = 'quiz')
            LEFT JOIN {tag_instance} ti2
                   ON ti2.itemid = cm.id
                   AND ti2.itemtype = 'course_modules'
                   AND ti2.component = 'core'
            LEFT JOIN {tag} t2
                   ON t2.id = ti2.tagid
            WHERE q.id = :quizid
        ";

        $params = ['quizid' => $quizid];
        $records = $DB->get_records_sql($sql, $params);

        $result = [];
        foreach ($records as $record) {
            $result[] = [
                'quizid'     => (int)$record->id,
                'quiz_name'  => $record->quiz_name,
                'tag_name'   => $record->tag_name_cm ?? '',
            ];
        }

        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'quizid'    => new external_value(PARAM_INT, 'Quiz ID'),
                'quiz_name' => new external_value(PARAM_TEXT, 'Quiz name'),
                'tag_name'  => new external_value(PARAM_RAW, 'Tag name (empty if none)'),
            ])
        );
    }
}