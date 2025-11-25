<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_completion_rate extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'    => new external_value(PARAM_INT, 'User ID'),
            'moduleid'  => new external_value(PARAM_INT, 'Module ID')
        ]);
    }

    public static function execute($userid, $moduleid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid' => $userid,
            'moduleid' => $moduleid
        ]);

        // 1. Lấy tất cả course_modules trong module
        $sql_modules = "
            SELECT cm.id AS cmid, cm.completion, cm.module
            FROM {course_modules} cm
            WHERE cm.id = :moduleid
              AND cm.completion > 0
        ";
        $modules = $DB->get_records_sql($sql_modules, ['moduleid' => $moduleid]);

        $completed_activities = [];
        $total_activities = count($modules);

        // 2. Duyệt từng activity để check completion
        foreach ($modules as $cm) {
            $completed = false;

            // Quiz đặc biệt: kiểm tra pass grade
            if ($cm->module == $DB->get_field('modules', 'id', ['name' => 'quiz'])) {
                $quizid = $DB->get_field('quiz', 'id', ['id' => $cm->instance]);
                $grade_item = $DB->get_record('grade_items', ['iteminstance' => $quizid, 'itemmodule' => 'quiz']);
                $grade = $DB->get_field('quiz_grades', 'grade', ['quiz' => $quizid, 'userid' => $userid]);

                if ($grade !== null && $grade >= $grade_item->gradepass) {
                    $completed = true;
                }

            } else {
                // Manual / automatic completion
                $cmc = $DB->get_record('course_modules_completion', ['coursemoduleid' => $cm->cmid, 'userid' => $userid]);
                if ($cmc && in_array($cmc->completionstate, [1,2])) {
                    $completed = true;
                }
            }

            if ($completed) {
                $completed_activities[] = $cm->cmid;
            }
        }

        // 3. Tính progress
        $progress = $total_activities > 0 ? round(count($completed_activities)/$total_activities, 4) : 0.0;

        // 4. Optional: thời gian spent, ví dụ cộng thời gian xem bài học
        $time_spent = 0; // cần custom logic nếu có tracking thời gian

        return [
            'userid' => $userid,
            'moduleid' => $moduleid,
            'progress' => $progress,
            'completed_activities' => $completed_activities,
            'total_activities' => $total_activities,
            'time_spent' => $time_spent
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'userid' => new external_value(PARAM_INT),
            'moduleid' => new external_value(PARAM_INT),
            'progress' => new external_value(PARAM_FLOAT),
            'completed_activities' => new external_multiple_structure(new external_value(PARAM_INT)),
            'total_activities' => new external_value(PARAM_INT),
            'time_spent' => new external_value(PARAM_INT)
        ]);
    }
}