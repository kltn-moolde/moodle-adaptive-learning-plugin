<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_total_resources_by_section extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'sectionid'      => new external_value(PARAM_INT, 'Section ID'),
            'objecttypes' => new external_multiple_structure(
                new external_value(PARAM_TEXT, 'Activity type like resource, hvp, quiz'),
                'List of activity types to count'
            )
        ]);
    }

    public static function execute($sectionid, $objecttypes) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'sectionid'      => $sectionid,
            'objecttypes' => $objecttypes
        ]);

        // Build IN clause placeholders
        list($inSql, $inParams) = $DB->get_in_or_equal($objecttypes, SQL_PARAMS_NAMED, 'param');

        $params = array_merge([
            'sectionid'   => $sectionid
        ], $inParams);

        $sql = "
            SELECT COUNT(*) AS total_resources
            FROM {course_modules} cm
            JOIN {modules} m ON cm.module = m.id
            WHERE cm.section = :sectionid
              AND m.name $inSql
        ";
        $count = $DB->get_field_sql($sql, $params);

        return [
            'total_resources' => (int)$count
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'total_resources' => new external_value(PARAM_INT, 'Total number of resources in the section')
        ]);
    }
}