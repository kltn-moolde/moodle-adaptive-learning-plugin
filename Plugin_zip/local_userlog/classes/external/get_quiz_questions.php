<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class get_quiz_questions extends external_api {

    /**
     * Tham số đầu vào
     */
    public static function execute_parameters() {
        return new external_function_parameters([
            'quizid' => new external_value(PARAM_INT, 'Quiz ID'),
        ]);
    }

    /**
     * Hàm chính
     */
    public static function execute($quizid) {
        global $DB;

        // Validate input
        self::validate_parameters(self::execute_parameters(), [
            'quizid' => $quizid
        ]);

        // SQL lấy thông tin câu hỏi trong quiz
        $sql = "
            SELECT 
                q.id AS question_id,
                q.name AS question_name,
                q.questiontext AS question_text,
                qs.maxmark AS question_maxmark,
                qc.name AS category_name,
                q.qtype AS question_type
            FROM {quiz_slots} qs
            JOIN {question_references} qr ON qr.itemid = qs.id
            JOIN {question_bank_entries} qbe ON qbe.id = qr.questionbankentryid
            JOIN {question_versions} qv ON qv.questionbankentryid = qbe.id
            JOIN {question} q ON q.id = qv.questionid
            JOIN {question_categories} qc ON qc.id = qbe.questioncategoryid
            WHERE qs.quizid = :quizid
            ORDER BY qs.slot
        ";

        $records = $DB->get_records_sql($sql, ['quizid' => $quizid]);

        // Build result array
        $result = [];
        foreach ($records as $r) {
            $result[] = [
                'question_id' => (int)$r->question_id,
                'question_name' => $r->question_name,
                'question_text' => $r->question_text,
                'question_maxmark' => (float)$r->question_maxmark,
                'category_name' => $r->category_name,
                'question_type' => $r->question_type,
            ];
        }

        return $result;
    }

    /**
     * Cấu trúc dữ liệu trả về
     */
    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'question_id' => new external_value(PARAM_INT, 'ID câu hỏi'),
                'question_name' => new external_value(PARAM_TEXT, 'Tên câu hỏi'),
                'question_text' => new external_value(PARAM_RAW, 'Nội dung câu hỏi (HTML)'),
                'question_maxmark' => new external_value(PARAM_FLOAT, 'Điểm tối đa của câu hỏi'),
                'category_name' => new external_value(PARAM_TEXT, 'Tên category'),
                'question_type' => new external_value(PARAM_TEXT, 'Loại câu hỏi (multichoice, essay,...)'),
            ])
        );
    }
}