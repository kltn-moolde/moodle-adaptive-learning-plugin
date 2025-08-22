<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class get_latest_quiz_pass_status_by_section extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'sectionid' => new external_value(PARAM_INT, 'Section ID'),
            'userid'    => new external_value(PARAM_INT, 'User ID')
        ]);
    }

    public static function execute($sectionid, $userid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'sectionid' => $sectionid,
            'userid'    => $userid
        ]);

        // ✅ Truyền đủ 3 tham số (sectionid, userid1, userid2)
        $params = [
            'sectionid' => $sectionid,
            'userid1'   => $userid,
            'userid2'   => $userid
        ];

        $sql = "
            SELECT 
                q.id AS quizid,
                cs.id AS sectionid,
                cs.name AS sectionname,
                ROUND(
                    (qa.sumgrades / q.sumgrades) * gi.grademax,
                    2
                ) AS last_grade,
                gi.gradepass,
                CASE
                    WHEN ROUND((qa.sumgrades / q.sumgrades) * gi.grademax, 2) >= COALESCE(gi.gradepass, 0) 
                    THEN 1 ELSE 0
                END AS is_passed
            FROM {course_sections} cs
            JOIN {course_modules} cm 
                ON cm.section = cs.id
            JOIN {modules} m 
                ON m.id = cm.module AND m.name = 'quiz'
            JOIN {quiz} q 
                ON q.id = cm.instance
            /* subquery: lấy thời gian attempt gần nhất cho từng quiz */
            JOIN (
                SELECT quiz, userid, MAX(timemodified) AS last_time
                FROM {quiz_attempts}
                WHERE state = 'finished'
                GROUP BY quiz, userid
            ) last_qa_time
                ON last_qa_time.quiz = q.id 
                AND last_qa_time.userid = :userid1
            JOIN {quiz_attempts} qa
                ON qa.quiz = last_qa_time.quiz
                AND qa.userid = last_qa_time.userid
                AND qa.timemodified = last_qa_time.last_time
            JOIN {grade_items} gi
                ON gi.iteminstance = q.id AND gi.itemmodule = 'quiz'
            WHERE cs.id = :sectionid
            AND qa.userid = :userid2
            ORDER BY qa.timemodified DESC
            LIMIT 1;
        ";

        $result = $DB->get_record_sql($sql, $params);

        // ✅ Tránh lỗi nếu không có kết quả
        if (!$result) {
            return [
                'sectionid'     => $sectionid,
                'sectionname'   => '',
                'quizid'        => 0,
                'is_passed'     => 0
            ];
        }

        return [
            'sectionid'     => $result->sectionid,
            'sectionname'   => $result->sectionname,
            'quizid'        => $result->quizid,
            'is_passed'     => $result->is_passed
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'sectionid'     => new external_value(PARAM_INT, 'Section ID'),
            'sectionname'   => new external_value(PARAM_TEXT, 'Section name'),
            'quizid'        => new external_value(PARAM_INT, 'Quiz ID'),
            'is_passed'     => new external_value(PARAM_INT, '1 if passed, 0 if not')
        ]);
    }
}