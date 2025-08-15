<?php
namespace local_userlog\external;

defined('MOODLE_INTERNAL') || die();
require_once("$CFG->libdir/externallib.php");
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/mod/quiz/lib.php');
require_once($CFG->dirroot . '/mod/quiz/locallib.php');

use external_api;
use external_function_parameters;
use external_single_structure;
use external_multiple_structure;
use external_value;

class create_quiz_from_categories extends external_api {

    private static function log_debug($message) {
        global $CFG;
        $logdir = $CFG->dataroot . '/local_userlog';
        if (!file_exists($logdir)) {
            mkdir($logdir, 0777, true);
        }
        $debuglog = $logdir . '/debug_create_quiz.txt';
        $time = date('Y-m-d H:i:s');
        file_put_contents($debuglog, "[$time] $message\n", FILE_APPEND | LOCK_EX);
    }

    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
            'quizname' => new external_value(PARAM_TEXT, 'Quiz name'),
            'userid' => new external_value(PARAM_INT, 'User ID'),
            'questions' => new external_multiple_structure(
                new external_single_structure([
                    'categoryid' => new external_value(PARAM_INT, 'Question category ID'),
                    'easy' => new external_value(PARAM_INT, 'Number of easy questions'),
                    'medium' => new external_value(PARAM_INT, 'Number of medium questions'),
                    'hard' => new external_value(PARAM_INT, 'Number of hard questions')
                ])
            )
        ]);
    }

    public static function execute($courseid, $quizname, $userid, $questions) {
        global $DB;

        try {
            self::log_debug("API called with courseid=$courseid, quizname=\"$quizname\"");
            self::log_debug("Questions payload: " . json_encode($questions, JSON_UNESCAPED_UNICODE));

            self::validate_parameters(self::execute_parameters(), [
                'courseid' => $courseid,
                'quizname' => $quizname,
                'userid' => $userid,
                'questions' => $questions
            ]);

            // 1. Lấy ID module quiz
            $moduleid = $DB->get_field('modules', 'id', ['name' => 'quiz'], MUST_EXIST);

            // 2. Tạo course module trước (instance tạm thời = 0)
            $cm = new \stdClass();
            $cm->course = $courseid;
            $cm->module = $moduleid;
            $cm->instance = 0; // sẽ cập nhật sau
            $cm->visible = 1;
            $cm->groupmode = 0;
            $cmid = add_course_module($cm);
            self::log_debug("Course module placeholder created with cmid={$cmid}");

            // 3. Chuẩn bị dữ liệu quiz
            $quiz = new \stdClass();
            $quiz->course = $courseid;
            $quiz->name = $quizname;
            $quiz->intro = '';
            $quiz->introformat = FORMAT_HTML;

            $quiz->timeopen = 0;
            $quiz->timeclose = 0;
            $quiz->timelimit = 0;
            $quiz->overduehandling = 'autosubmit';
            $quiz->graceperiod = 0;

            $quiz->preferredbehaviour = 'deferredfeedback';
            $quiz->canredoquestions = 0;
            $quiz->attempts = 0;
            $quiz->attemptonlast = 0;
            $quiz->grademethod = 1;

            $quiz->decimalpoints = 2;
            $quiz->questiondecimalpoints = -1;

            $CONST_REVIEW_1 = 69888;
            $CONST_REVIEW_2 = 4352;
            $quiz->reviewattempt = $CONST_REVIEW_1;
            $quiz->reviewcorrectness = $CONST_REVIEW_2;
            $quiz->reviewmaxmarks = $CONST_REVIEW_1;
            $quiz->reviewmarks = $CONST_REVIEW_2;
            $quiz->reviewspecificfeedback = $CONST_REVIEW_2;
            $quiz->reviewgeneralfeedback = $CONST_REVIEW_2;
            $quiz->reviewrightanswer = $CONST_REVIEW_2;
            $quiz->reviewoverallfeedback = $CONST_REVIEW_2;

            $quiz->questionsperpage = 1;
            $quiz->navmethod = 'free';
            $quiz->shuffleanswers = 1;

            $quiz->sumgrades = 0;
            $quiz->grade = 10.0;

            $quiz->timecreated = time();
            $quiz->timemodified = time();

            $quiz->password = '';
            $quiz->quizpassword = ''; // truong nay hoi bat on
            $quiz->subnet = '';
            $quiz->browsersecurity = '-';

            $quiz->delay1 = 0;
            $quiz->delay2 = 0;

            $quiz->showuserpicture = 0;
            $quiz->showblocks = 0;

            $quiz->completionattemptsexhausted = 0;
            $quiz->completionminattempts = 0;
            $quiz->allowofflineattempts = 0;
            $quiz->precreateattempts = 0;

            // Quan trọng: Gán coursemodule trước khi gọi quiz_add_instance()
            $quiz->coursemodule = $cmid;

            // 4. Tạo quiz
            $quizid = quiz_add_instance($quiz, null);
            $quiz->id = $quizid;
            $DB->update_record('quiz', [
                'id' => $quizid,
                'reviewattempt' => $CONST_REVIEW_1,
                'reviewcorrectness' => $CONST_REVIEW_2,
                'reviewmaxmarks' => $CONST_REVIEW_1,
                'reviewmarks' => $CONST_REVIEW_2,
                'reviewspecificfeedback' => $CONST_REVIEW_2,
                'reviewgeneralfeedback' => $CONST_REVIEW_2,
                'reviewrightanswer' => $CONST_REVIEW_2,
                'reviewoverallfeedback' => $CONST_REVIEW_2
            ]);
            self::log_debug("Quiz created with id={$quiz->id}");

            // 🔹 Thêm đoạn này để cập nhật gradepass
            $gradeitem = $DB->get_record('grade_items', [
                'itemtype' => 'mod',
                'itemmodule' => 'quiz',
                'iteminstance' => $quizid,
                'courseid' => $courseid
            ], '*', IGNORE_MISSING);

            if ($gradeitem) {
                $gradeitem->gradepass = 5; // điểm đạt
                $DB->update_record('grade_items', $gradeitem);
                self::log_debug("Updated gradepass=5 for grade_item id={$gradeitem->id}");
            } else {
                self::log_debug("Grade item for quiz {$quizid} not found, cannot set gradepass");
            }

            // 5. Cập nhật instance cho course module
            $DB->set_field('course_modules', 'instance', $quizid, ['id' => $cmid]);
            course_add_cm_to_section($courseid, $cmid, 0);
            self::log_debug("Course module updated with instance={$quizid}");

            // 6. Lấy câu hỏi và thêm vào quiz
            foreach ($questions as $qcat) {
                foreach (['easy', 'medium', 'hard'] as $level) {
                    $count = (int)$qcat[$level];
                    if ($count > 0) {
                        self::log_debug("Fetching {$count} '{$level}' questions from category {$qcat['categoryid']}");
                        $selected = self::get_random_questions_by_tag($qcat['categoryid'], $level, $count);
                        self::log_debug("Selected question IDs: " . json_encode($selected));
                        foreach ($selected as $qid) {
                            self::quiz_add_quiz_question($qid, $quiz);
                        }
                    }
                }
            }

            // 7. Cập nhật tổng điểm quiz
            quiz_update_sumgrades($quiz);

            // 8. chỉ user chi dinh moi duoc xem quiz
            self::restrict_quiz_to_user($quiz->id, $userid);

            $result = [
                'quizid' => $quiz->id,
                'cmid' => $cmid
            ];

            self::log_debug("Execution finished. Result: " . json_encode($result));
            return $result;

        } catch (\Exception $e) {
            global $DB;
            $lastsql = method_exists($DB, 'get_last_sql') ? $DB->get_last_sql() : '[N/A]';
            $dberr = method_exists($DB, 'get_last_error') ? $DB->get_last_error() : '';
            self::log_debug("[FATAL ERROR] " . $e->getMessage());
            self::log_debug("[LAST SQL] " . $lastsql);
            if ($dberr) {
                self::log_debug("[DB ERROR MESSAGE] " . $dberr);
            }
            self::log_debug("[TRACE] " . $e->getTraceAsString());
            throw $e;
        }
    }

    private static function restrict_quiz_to_user($quizid, $userid) {
        global $DB;

        $courseid = $DB->get_field('quiz', 'course', ['id' => $quizid], MUST_EXIST);
        $groupname = 'quiz_'.$quizid.'_user_'.$userid;

        // 1. Tạo hoặc lấy group
        if (!$groupid = $DB->get_field('groups', 'id', ['courseid' => $courseid, 'name' => $groupname])) {
            $groupdata = (object)[
                'courseid' => $courseid,
                'name' => $groupname,
                'timecreated' => time(),
                'timemodified' => time()
            ];
            $groupid = $DB->insert_record('groups', $groupdata);
        }

        // 2. Thêm user vào group (nếu chưa có)
        if (!$DB->record_exists('groups_members', ['groupid' => $groupid, 'userid' => $userid])) {
            $groupmember = (object)[
                'groupid' => $groupid,
                'userid' => $userid,
                'timeadded' => time()
            ];
            $DB->insert_record('groups_members', $groupmember);
        }

        // 3. Tạo điều kiện giới hạn availability dựa trên group
        $restriction = [
                'op' => '&',
                'show' => false,   
                'c' => [
                    [
                        'type' => 'group',
                        'id' => $groupid,
                        'show' => true,  
                    ]
                ],
                'showc' => [false],
            ];

        // 4. Update course_modules.availability
        $moduleid = $DB->get_field('modules', 'id', ['name' => 'quiz'], MUST_EXIST);
        $cmid = $DB->get_field('course_modules', 'id', ['instance' => $quizid, 'module' => $moduleid], MUST_EXIST);
        $cm = $DB->get_record('course_modules', ['id' => $cmid], '*', MUST_EXIST);
        $cm->availability = json_encode($restriction);
        $DB->update_record('course_modules', $cm);
    }

    private static function get_random_questions_by_tag($categoryid, $tagname, $limit) {
        global $DB;
        try {
            $sql = "
                SELECT q.id
                FROM {question} q
                INNER JOIN {question_versions} qv ON qv.questionid = q.id
                INNER JOIN {question_bank_entries} qbe ON qbe.id = qv.questionbankentryid
                INNER JOIN {question_categories} qc ON qc.id = qbe.questioncategoryid
                JOIN {tag_instance} ti ON ti.itemid = q.id
                JOIN {tag} t ON t.id = ti.tagid
                WHERE LOWER(t.name) = :tagname
                  AND qc.id = :categoryid
                  AND ti.itemtype = 'question'
                  AND q.qtype = 'multichoice'
            ";

            $params = [
                'categoryid' => $categoryid,
                'tagname' => strtolower($tagname)
            ];

            $qids = $DB->get_fieldset_sql($sql, $params);
            shuffle($qids);
            return array_slice($qids, 0, $limit);

        } catch (\Exception $e) {
            global $DB;
            $lastsql = method_exists($DB, 'get_last_sql') ? $DB->get_last_sql() : '[N/A]';
            $dberr = method_exists($DB, 'get_last_error') ? $DB->get_last_error() : '';
            self::log_debug("[DB ERROR in get_random_questions_by_tag] " . $e->getMessage());
            self::log_debug("[LAST SQL] " . $lastsql);
            if ($dberr) {
                self::log_debug("[DB ERROR MESSAGE] " . $dberr);
            }
            throw $e;
        }
    }

    private static function quiz_add_quiz_question($questionid, $quiz) {
        try {
            quiz_add_quiz_question($questionid, $quiz, 1.0);
            self::log_debug("Added question ID {$questionid} to quiz ID {$quiz->id} with maxmark=1.0");
        } catch (\Exception $e) {
            global $DB;
            $lastsql = method_exists($DB, 'get_last_sql') ? $DB->get_last_sql() : '[N/A]';
            $dberr = method_exists($DB, 'get_last_error') ? $DB->get_last_error() : '';
            self::log_debug("[DB ERROR in quiz_add_quiz_question] " . $e->getMessage());
            self::log_debug("[LAST SQL] " . $lastsql);
            if ($dberr) {
                self::log_debug("[DB ERROR MESSAGE] " . $dberr);
            }
            throw $e;
        }
    }

    public static function execute_returns() {
        return new external_single_structure([
            'quizid' => new external_value(PARAM_INT, 'Created quiz ID'),
            'cmid' => new external_value(PARAM_INT, 'Course module ID')
        ]);
    }
}