<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

// LOG GLOBAL - TEST XEM FILE CÓ ĐƯỢC LOAD KHÔNG
file_put_contents('/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/debug.txt', 
    "FILE LOADED: " . __FILE__ . " at " . date('Y-m-d H:i:s') . "\n", FILE_APPEND);


class get_user_logs extends external_api {

    // ============================
    // 1. DECLARE PARAMETERS
    // ============================
    public static function execute_parameters() {
        return new external_function_parameters(
            [
                'userid'     => new external_value(PARAM_INT, 'User ID'),
                'courseid'   => new external_value(PARAM_INT, 'Course ID'),
                'moduleid'   => new external_value(PARAM_INT, 'Parent module (section) ID'),
                'starttime'  => new external_value(PARAM_INT, 'Start time timestamp', VALUE_OPTIONAL),
                'endtime'    => new external_value(PARAM_INT, 'End time timestamp', VALUE_OPTIONAL)
            ]
        );
    }

    // ============================
    // 2. MAIN FUNCTION
    // ============================
    public static function execute($userid, $courseid, $moduleid, $starttime = 0, $endtime = 0) {
        global $DB;

        // Validate parameters
        $params = self::validate_parameters(self::execute_parameters(), [
            'userid'    => $userid,
            'courseid'  => $courseid,
            'moduleid'  => $moduleid,
            'starttime' => $starttime,
            'endtime'   => $endtime
        ]);

        // Default time range: last 7 days
        if ($params['endtime'] == 0) {
            $params['endtime'] = time();
        }
        if ($params['starttime'] == 0) {
            $params['starttime'] = $params['endtime'] - 7 * 24 * 3600;
        }

        // ============================
        // 3. STEP 1 — GET CMID LIST
        // ============================

        $sql_cm = "
            SELECT cm.id AS cmid
            FROM {course_modules} cm
            WHERE cm.course = :courseid
              AND cm.section = :moduleid
        ";

        $cm_records = $DB->get_records_sql($sql_cm, [
            'courseid' => $courseid,
            'moduleid' => $moduleid
        ]);

        if (empty($cm_records)) {
            return ['logs' => []];
        }

        // Extract cmid array
        $cmids = array_map(fn($c) => $c->cmid, $cm_records);

        list($in_sql, $in_params) = $DB->get_in_or_equal($cmids, SQL_PARAMS_NAMED);

        // ============================
        // 4. STEP 2 — GET LOGS
        // ============================

        $sql_logs = "
            SELECT 
                l.id,
                l.userid,
                l.courseid,
                l.contextinstanceid,
                l.action,
                l.eventname,
                l.timecreated,
                l.other
            FROM {logstore_standard_log} l
            WHERE l.userid = :userid
              AND l.courseid = :courseid
              AND l.timecreated BETWEEN :starttime AND :endtime
              AND l.contextinstanceid $in_sql
            ORDER BY l.timecreated DESC
        ";

        $log_params = array_merge([
            'userid'     => $userid,
            'courseid'   => $courseid,
            'starttime'  => $params['starttime'],
            'endtime'    => $params['endtime']
        ], $in_params);

        $logs = $DB->get_records_sql($sql_logs, $log_params);

        // Format output
        $output = [];
        foreach ($logs as $log) {
            $output[] = [
                'id'                => $log->id,
                'userid'            => $log->userid,
                'courseid'          => $log->courseid,
                'contextinstanceid' => $log->contextinstanceid,
                'action'            => $log->action,
                'eventname'         => $log->eventname,
                'timecreated'       => $log->timecreated,
                'other'             => $log->other
            ];
        }

        return ['logs' => $output];
    }

    // ============================
    // 5. RETURN STRUCTURE
    // ============================
    public static function execute_returns() {
        return new external_single_structure([
            'logs' => new external_multiple_structure(
                new external_single_structure([
                    'id'                => new external_value(PARAM_INT, 'Log ID'),
                    'userid'            => new external_value(PARAM_INT, 'User ID'),
                    'courseid'          => new external_value(PARAM_INT, 'Course ID'),
                    'contextinstanceid' => new external_value(PARAM_INT, 'Module instance ID'),
                    'action'            => new external_value(PARAM_TEXT, 'Action'),
                    'eventname'         => new external_value(PARAM_TEXT, 'Event name'),
                    'timecreated'       => new external_value(PARAM_INT, 'Log timestamp'),
                    'other'             => new external_value(PARAM_RAW, 'Other raw data', VALUE_OPTIONAL)
                ])
            )
        ]);
    }
}