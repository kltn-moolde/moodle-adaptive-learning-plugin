<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class get_user_section_avg_grade extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'    => new external_value(PARAM_INT, 'User ID'),
            'sectionid' => new external_value(PARAM_INT, 'Section ID'),
            'courseid'  => new external_value(PARAM_INT, 'Course ID'),
        ]);
    }

    public static function execute($userid, $sectionid, $courseid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid'    => $userid,
            'sectionid' => $sectionid,
            'courseid'  => $courseid
        ]);

        $sql = "
            SELECT cs.id AS section_id,
                   cs.section AS section_number,
                   AVG(g.grade) AS avg_section_grade
            FROM {course_sections} cs
            JOIN {course_modules} cm 
                   ON cm.section = cs.id
            JOIN {modules} m 
                   ON m.id = cm.module
            JOIN {quiz} q 
                   ON q.id = cm.instance AND m.name = 'quiz'
            JOIN {quiz_grades} g 
                   ON g.quiz = q.id
            WHERE cs.course = :courseid
              AND g.userid = :userid
              AND cs.id = :sectionid
            GROUP BY cs.id, cs.section
            ORDER BY cs.section
        ";

        $params = [
            'userid'    => $userid,
            'courseid'  => $courseid,
            'sectionid' => $sectionid
        ];

        $record = $DB->get_record_sql($sql, $params);

        if (!$record) {
            return [
                'section_id'       => (int)$sectionid,
                'section_number'   => null,
                'avg_section_grade'=> null
            ];
        }

        return [
            'section_id'       => (int)$record->section_id,
            'section_number'   => (int)$record->section_number,
            'avg_section_grade'=> (float)$record->avg_section_grade
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'section_id'        => new external_value(PARAM_INT,  'Section ID'),
            'section_number'    => new external_value(PARAM_INT,  'Section number', VALUE_OPTIONAL),
            'avg_section_grade' => new external_value(PARAM_FLOAT,'Average grade (null if none)', VALUE_OPTIONAL),
        ]);
    }
}