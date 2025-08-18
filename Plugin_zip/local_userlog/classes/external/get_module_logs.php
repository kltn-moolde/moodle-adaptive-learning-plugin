<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_module_logs extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'cmid' => new external_value(PARAM_INT, 'Course module ID'),
            'limit' => new external_value(PARAM_INT, 'Limit results', VALUE_DEFAULT, 20),
        ]);
    }

    public static function execute($cmid, $limit = 20) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), ['cmid' => $cmid, 'limit' => $limit]);

        $sql = "
            SELECT l.id, l.userid, u.firstname, u.lastname, l.eventname, l.action, l.target, l.component, l.timecreated
            FROM {logstore_standard_log} l
            JOIN {user} u ON u.id = l.userid
            WHERE l.contextinstanceid = :cmid
            ORDER BY l.timecreated DESC
        ";
        $logs = $DB->get_records_sql($sql, ['cmid' => $cmid], 0, $limit);

        $result = [];
        foreach ($logs as $log) {
            $result[] = [
                'id' => $log->id,
                'userid' => $log->userid,
                'username' => fullname($log),
                'eventname' => $log->eventname,
                'action' => $log->action,
                'target' => $log->target,
                'component' => $log->component,
                'timecreated' => $log->timecreated
            ];
        }

        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'id' => new external_value(PARAM_INT),
                'userid' => new external_value(PARAM_INT),
                'username' => new external_value(PARAM_TEXT),
                'eventname' => new external_value(PARAM_TEXT),
                'action' => new external_value(PARAM_TEXT),
                'target' => new external_value(PARAM_TEXT),
                'component' => new external_value(PARAM_TEXT),
                'timecreated' => new external_value(PARAM_INT)
            ])
        );
    }
}