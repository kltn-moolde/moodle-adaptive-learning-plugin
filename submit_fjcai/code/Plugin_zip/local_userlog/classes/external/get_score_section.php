<?php
namespace local_userlog\external;

// LOG GLOBAL - TEST XEM FILE CÓ ĐƯỢC LOAD KHÔNG
file_put_contents(
    '/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/debug.txt',
    "FILE LOADED: " . __FILE__ . " at " . date('Y-m-d H:i:s') . "\n",
    FILE_APPEND
);

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_score_section extends external_api
{
    public static function execute_parameters()
    {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User ID'),
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
            'sectionid' => new external_value(PARAM_INT, 'Section ID')
        ]);
    }

    public static function execute($userid, $courseid, $sectionid)
    {
        global $DB;

        $logfile = '/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/debug.txt';

        file_put_contents($logfile, "\n==== FUNCTION CALLED ====\n", FILE_APPEND);
        file_put_contents($logfile, "Received: userid=$userid, courseid=$courseid, sectionid=$sectionid\n", FILE_APPEND);

        self::validate_parameters(self::execute_parameters(), [
            'userid' => $userid,
            'courseid' => $courseid,
            'sectionid' => $sectionid
        ]);

        file_put_contents($logfile, "✓ Validation passed\n", FILE_APPEND);

        $params = [
            'userid1'   => $userid,
            'userid2'   => $userid,
            'userid3'   => $userid,
            'userid4'   => $userid,
            'courseid'  => $courseid,
            'sectionid' => $sectionid
        ];

        // --- SQL giống 100% Workbench ---
        $sql = "
            SELECT 
                cm.id AS moduleid,
                q.id AS quizid,
                q.name AS activityname,
                'quiz' AS activitytype,
                COALESCE(qg.grade / gi.grademax, 0) AS score,
                COALESCE(qg.grade, 0) AS rawscore,
                gi.grademax AS maxscore,
                COALESCE(qa.max_attempt, 0) AS attempt,
                COALESCE(cmc.timemodified, 0) AS timecompleted
            FROM {course_modules} AS cm
            JOIN {modules} AS modn 
                ON modn.id = cm.module
            JOIN {quiz} AS q 
                ON q.id = cm.instance 
                AND modn.name = 'quiz'
            LEFT JOIN {grade_items} AS gi 
                ON gi.iteminstance = q.id 
                AND gi.itemmodule = 'quiz'
            LEFT JOIN {quiz_grades} AS qg 
                ON qg.quiz = q.id 
                AND qg.userid = :userid1
            LEFT JOIN (
                SELECT quiz, userid, MAX(attempt) AS max_attempt
                FROM {quiz_attempts}
                WHERE userid = :userid2
                GROUP BY quiz, userid
            ) qa 
                ON qa.quiz = q.id 
                AND qa.userid = :userid3
            LEFT JOIN {course_modules_completion} AS cmc 
                ON cmc.coursemoduleid = cm.id 
                AND cmc.userid = :userid4
            WHERE cm.course = :courseid
              AND modn.name = 'quiz'
              AND cm.section = :sectionid
        ";

        file_put_contents($logfile, "--- SQL ---\n$sql\n", FILE_APPEND);
        file_put_contents($logfile, "--- PARAMS ---\n" . json_encode($params, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);

        try {
            $records = $DB->get_records_sql($sql, $params);
            file_put_contents($logfile, "--- RAW DB RESULT ---\n" . json_encode($records, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);
        } catch (\Exception $e) {
            file_put_contents($logfile, "--- SQL ERROR ---\n" . $e->getMessage() . "\n", FILE_APPEND);
            throw $e;
        }

        $result = [];
        foreach ($records as $r) {
            $result[] = [
                'moduleid'      => (int) $r->moduleid,
                'activityid'    => (int) $r->quizid,
                'activityname'  => $r->activityname,
                'activitytype'  => $r->activitytype,
                'score'         => (float) $r->score,
                'rawscore'      => (float) $r->rawscore,
                'maxscore'      => (float) $r->maxscore,
                'attempt'       => (int) $r->attempt,
                'timecompleted' => (int) $r->timecompleted
            ];
        }

        file_put_contents($logfile, "--- FINAL RESULT ---\n" . json_encode($result, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);

        return ['scores' => $result];
    }

    public static function execute_returns()
    {
        return new external_single_structure([
            'scores' => new external_multiple_structure(
                new external_single_structure([
                    'moduleid'      => new external_value(PARAM_INT),
                    'activityid'    => new external_value(PARAM_INT),
                    'activityname'  => new external_value(PARAM_TEXT),
                    'activitytype'  => new external_value(PARAM_TEXT),
                    'score'         => new external_value(PARAM_FLOAT),
                    'rawscore'      => new external_value(PARAM_FLOAT),
                    'maxscore'      => new external_value(PARAM_FLOAT),
                    'attempt'       => new external_value(PARAM_INT),
                    'timecompleted' => new external_value(PARAM_INT)
                ])
            )
        ]);
    }
}