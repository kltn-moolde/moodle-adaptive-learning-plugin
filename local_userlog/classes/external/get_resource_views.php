<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_resource_views extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'      => new external_value(PARAM_INT, 'User ID'),
            'courseid'    => new external_value(PARAM_INT, 'Course ID'),
            'objecttypes' => new external_multiple_structure(
                new external_value(PARAM_TEXT, 'Activity type like resource, hvp, quiz'),
                'List of activity types to count'
            )
        ]);
    }

    public static function execute($userid, $courseid, $objecttypes) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid'      => $userid,
            'courseid'    => $courseid,
            'objecttypes' => $objecttypes
        ]);

        // Build IN clause placeholders
        list($inSql, $inParams) = $DB->get_in_or_equal($objecttypes, SQL_PARAMS_NAMED, 'param');

        $params = array_merge([
            'userid'   => $userid,
            'courseid' => $courseid
        ], $inParams);

        $sql = "
            SELECT COUNT(*) AS resource_views
            FROM {logstore_standard_log} l
            WHERE l.userid = :userid
              AND l.courseid = :courseid
              AND l.objecttable $inSql
              AND l.action = 'viewed'
        ";

        $views = $DB->get_field_sql($sql, $params);

        return [
            'resource_views' => (int)$views
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'resource_views' => new external_value(PARAM_INT, 'Number of resource views')
        ]);
    }
}