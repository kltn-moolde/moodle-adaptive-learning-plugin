<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();

require_once("$CFG->libdir/externallib.php");
require_once($CFG->dirroot . '/question/format.php');
require_once($CFG->dirroot . '/question/format/xml/format.php');
require_once($CFG->libdir . '/questionlib.php');

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;
use external_multiple_structure;
use context;
use moodle_exception;
use qformat_xml;

class import_questions_from_xml extends external_api {

    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid'   => new external_value(PARAM_INT, 'ID của khóa học chứa category'),
            'xmlcontent' => new external_value(PARAM_RAW, 'Nội dung file XML (Moodle XML format) dưới dạng chuỗi'),
        ]);
    }

    public static function execute($courseid, $xmlcontent) {
        global $DB;

        $params = self::validate_parameters(self::execute_parameters(), [
            'courseid'   => $courseid,
            'xmlcontent' => $xmlcontent
        ]);

        // Tìm question category phù hợp trong khóa học
        $sql = "SELECT qc.id AS categoryid, qc.contextid, ctx.instanceid
                FROM {question_categories} qc
                JOIN {context} ctx ON qc.contextid = ctx.id
                JOIN {course_modules} cm ON ctx.instanceid = cm.id AND ctx.contextlevel = 70
                JOIN {course} c ON cm.course = c.id
                WHERE qc.info IS NOT NULL
                  AND qc.info <> ''
                  AND c.id = :courseid
                ORDER BY qc.id ASC
                LIMIT 1";

        $cat = $DB->get_record_sql($sql, ['courseid' => $params['courseid']]);
        if (!$cat) {
            throw new moodle_exception('nocategory', 'local_userlog', '', 'Không tìm thấy category phù hợp cho courseid');
        }

        $category = $DB->get_record('question_categories', ['id' => $cat->categoryid], '*', MUST_EXIST);
        $context  = context::instance_by_id($cat->contextid, MUST_EXIST);

        // Tạo file tạm để import
        $tmpdir  = make_temp_directory('questionimport');
        $tmpfile = $tmpdir . '/import_' . time() . '_' . uniqid() . '.xml';
        file_put_contents($tmpfile, $params['xmlcontent']);

        try {
            $importer = new qformat_xml();
            $importer->setFilename($tmpfile);
            $importer->setCategory($category);
            $importer->setCatfromfile(false);
            $importer->setStoponerror(true);

            if (!$importer->importprocess()) {
                $errors = $importer->get_errors() ?: ['Unknown import error'];
                @unlink($tmpfile);
                throw new moodle_exception('importerror', 'question', '', implode('; ', $errors));
            }

            $importedcount = count($importer->questions ?? []);

            @unlink($tmpfile);

            return [
                'success'       => true,
                'importedcount' => $importedcount,
                'categoryid'    => $category->id,
                'instanceid'    => $cat->instanceid,
                'warnings'      => []
            ];

        } catch (\Exception $e) {
            @unlink($tmpfile);
            throw $e;
        }
    }

    public static function execute_returns() {
        return new external_single_structure([
            'success'       => new external_value(PARAM_BOOL, 'Thành công hay không'),
            'importedcount' => new external_value(PARAM_INT, 'Số câu hỏi đã import'),
            'categoryid'    => new external_value(PARAM_INT, 'Category ID đã import vào'),
            'instanceid'    => new external_value(PARAM_INT, 'ID của module (instanceid)'),
            'warnings'      => new external_multiple_structure(
                new external_value(PARAM_TEXT, 'Cảnh báo nếu có'),
                'Danh sách cảnh báo',
                VALUE_OPTIONAL,
                []
            ),
        ]);
    }
}