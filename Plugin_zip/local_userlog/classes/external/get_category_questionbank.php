<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class get_category_questionbank extends external_api {
    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
        ]);
    }

    public static function execute($courseid) {
        global $DB;

        self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid
        ]);

        $sql = "
           SELECT
                qc.id AS categoryid,
                qc.name AS categoryname,
                qc.parent AS parentid
            FROM {question_categories} qc
            JOIN {context} ctx 
                ON ctx.id = qc.contextid
            LEFT JOIN {course_modules} cm
                ON ctx.contextlevel = 70 AND cm.id = ctx.instanceid
            LEFT JOIN {course} c
                ON ctx.contextlevel = 70 AND c.id = cm.course
            WHERE      
                c.id = :courseid
                AND qc.name NOT LIKE 'Default %'
                AND LOWER(qc.name) <> 'top'
            ORDER BY qc.parent, qc.sortorder;
        ";

        $params = ['courseid' => $courseid];
        $records = $DB->get_records_sql($sql, $params);

        $indexedCategories = [];
        $rootCategories = [];
        
        // Bước 1 & 2: Lặp qua các bản ghi để lập chỉ mục và tìm các danh mục gốc
        foreach ($records as $record) {
            $category = [
                'categoryid' => (int)$record->categoryid,
                'categoryname' => $record->categoryname,
                'parentid' => (int)$record->parentid
            ];
            $indexedCategories[$record->categoryid] = $category;
            // Nếu parentid không tồn tại trong danh sách các categoryid, nó là một root category
            if (!isset($indexedCategories[$record->parentid])) {
                 $rootCategories[$record->categoryid] = $category;
            }
        }
        
        // Bước 3: Tìm chính xác các danh mục gốc
        $finalRootCategories = [];
        foreach($indexedCategories as $categoryId => $category) {
            if (!isset($indexedCategories[$category['parentid']])) {
                $finalRootCategories[] = $category;
            }
        }
        
        // Xây dựng cây phân cấp từ các danh mục gốc
        $result = [];
        foreach ($finalRootCategories as $root) {
            $result[] = self::buildTree($indexedCategories, $root['categoryid']);
        }

        return $result;
    }
    
    /**
     * Hàm đệ quy để xây dựng cấu trúc cây.
     *
     * @param array $indexedCategories Danh sách các danh mục đã được lập chỉ mục.
     * @param int $parentId ID của danh mục cha.
     * @return array Cấu trúc cây con.
     */
    private static function buildTree(&$indexedCategories, $parentId) {
        $branch = $indexedCategories[$parentId];
        $children = [];
        
        foreach ($indexedCategories as $category) {
            if ($category['parentid'] === $parentId) {
                // Đệ quy để tìm con của danh mục con
                $children[] = self::buildTree($indexedCategories, $category['categoryid']);
            }
        }
        
        $branch['children'] = $children; // luôn tồn tại, có thể là []

        return $branch;
    }

    public static function execute_returns() {
        return new external_multiple_structure(
            new external_single_structure([
                'categoryid' => new external_value(PARAM_INT, 'Category ID'),
                'categoryname' => new external_value(PARAM_TEXT, 'Category Name'),
                'parentid' => new external_value(PARAM_INT, 'Parent Category ID'),
                'children' => new external_multiple_structure(
                    new external_single_structure([
                        'categoryid' => new external_value(PARAM_INT, 'Category ID'),
                        'categoryname' => new external_value(PARAM_TEXT, 'Category Name'),
                        'parentid' => new external_value(PARAM_INT, 'Parent Category ID'),
                        // Định nghĩa đệ quy cho 'children'
                        'children' => new external_multiple_structure(
                            new external_single_structure([
                                'categoryid' => new external_value(PARAM_INT, 'Category ID'),
                                'categoryname' => new external_value(PARAM_TEXT, 'Category Name'),
                                'parentid' => new external_value(PARAM_INT, 'Parent Category ID')
                            ]),
                            'Nested children'
                        )
                    ]),
                    'Children categories'
                ),
            ])
        );
    }
}
