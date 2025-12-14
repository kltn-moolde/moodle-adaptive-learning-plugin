<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_viewed_resources_distinct_by_section extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'userid'      => new external_value(PARAM_INT, 'User ID'),
            'courseid'    => new external_value(PARAM_INT, 'Course ID'),
            'sectionid'   => new external_value(PARAM_INT, 'Section ID'),
            'objecttypes' => new external_multiple_structure(
                new external_value(PARAM_TEXT, 'Activity type like resource, hvp, quiz'),
                'List of activity types to check'
            )
        ]);
    }

    public static function execute($userid, $courseid, $sectionid, $objecttypes) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'userid'      => $userid,
            'courseid'    => $courseid,
            'sectionid'   => $sectionid,
            'objecttypes' => $objecttypes
        ]);

        // ⚠️ Tách riêng điều kiện cho l.objecttable và m.name
        list($inSql1, $inParams1) = $DB->get_in_or_equal($objecttypes, SQL_PARAMS_NAMED, 'obj');
        list($inSql2, $inParams2) = $DB->get_in_or_equal($objecttypes, SQL_PARAMS_NAMED, 'mod');

        $params = array_merge([
            'userid'    => $userid,
            'courseid'  => $courseid,
            'sectionid' => $sectionid
        ], $inParams1, $inParams2);

        $sql = "
            SELECT COUNT(DISTINCT l.contextinstanceid) AS viewed_resources
            FROM {logstore_standard_log} l
            JOIN {course_modules} cm ON l.contextinstanceid = cm.id
            JOIN {modules} m ON cm.module = m.id
            JOIN {course_sections} cs ON cm.section = cs.id
            WHERE l.userid = :userid
              AND l.courseid = :courseid
              AND cs.id = :sectionid
              AND l.action = 'viewed'
              AND l.objecttable $inSql1
              AND m.name $inSql2
        ";

        $count = $DB->get_field_sql($sql, $params);

        return [
            'viewed_resources' => (int)$count
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'viewed_resources' => new external_value(PARAM_INT, 'Number of resources viewed in the section')
        ]);
    }
}