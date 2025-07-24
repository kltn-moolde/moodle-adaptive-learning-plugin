<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_user_logs extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User ID'),
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
            'limit' => new external_value(PARAM_INT, 'Limit results', VALUE_DEFAULT, 20),
        ]);
    }

    public static function execute($userid, $courseid, $limit = 20) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), ['userid' => $userid, 'courseid' => $courseid, 'limit' => $limit]);

        $sql = "
            SELECT 
                l.id, l.eventname, l.component, l.action, l.target, l.objecttable, l.objectid, 
                l.crud, l.edulevel, l.contextid, l.contextlevel, l.contextinstanceid, 
                l.userid, l.courseid, l.relateduserid, l.anonymous, l.other, l.timecreated, 
                l.origin, l.ip, l.realuserid
            FROM {logstore_standard_log} l
            WHERE l.userid = :userid AND l.courseid = :courseid
            ORDER BY l.timecreated DESC
        ";

        $logs = $DB->get_records_sql($sql, ['userid' => $userid, 'courseid' => $courseid], 0, $limit);

        $result = [];
        foreach ($logs as $log) {
            $result[] = [
            'id' => $log->id,
            'eventname' => $log->eventname,
            'component' => $log->component,
            'action' => $log->action,
            'target' => $log->target,
            'objecttable' => $log->objecttable,
            'objectid' => $log->objectid,
            'crud' => $log->crud,
            'edulevel' => $log->edulevel,
            'contextid' => $log->contextid,
            'contextlevel' => $log->contextlevel,
            'contextinstanceid' => $log->contextinstanceid,
            'userid' => $log->userid,
            'courseid' => $log->courseid,
            'relateduserid' => $log->relateduserid ?? null,
            'anonymous' => $log->anonymous,
            'other' => $log->other ?? '',
            'timecreated' => $log->timecreated,
            'origin' => $log->origin,
            'ip' => $log->ip,
            'realuserid' => $log->realuserid ?? null
];
        }

        return $result;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'id' => new external_value(PARAM_INT),
                'eventname' => new external_value(PARAM_TEXT),
                'component' => new external_value(PARAM_TEXT),
                'action' => new external_value(PARAM_TEXT),
                'target' => new external_value(PARAM_TEXT),
                'objecttable' => new external_value(PARAM_TEXT),
                'objectid' => new external_value(PARAM_INT),
                'crud' => new external_value(PARAM_TEXT),
                'edulevel' => new external_value(PARAM_INT),
                'contextid' => new external_value(PARAM_INT),
                'contextlevel' => new external_value(PARAM_INT),
                'contextinstanceid' => new external_value(PARAM_INT),
                'userid' => new external_value(PARAM_INT),
                'courseid' => new external_value(PARAM_INT),
                'relateduserid' => new external_value(PARAM_INT, 'Related user ID', VALUE_OPTIONAL),
                'anonymous' => new external_value(PARAM_INT),
                'other' => new external_value(PARAM_RAW, 'Other (JSON)'),
                'timecreated' => new external_value(PARAM_INT),
                'origin' => new external_value(PARAM_TEXT),
                'ip' => new external_value(PARAM_TEXT),
                'realuserid' => new external_value(PARAM_INT, 'Real user ID', VALUE_OPTIONAL)
            ])
        );
    }
}