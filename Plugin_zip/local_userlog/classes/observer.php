<?php
namespace local_userlog;

defined('MOODLE_INTERNAL') || die();

class observer {

    public static function any_event(\core\event\base $event) {
        global $CFG;

        // Path file log
        $logfile = '/Users/nguyenhuuloc/Documents/MyComputer/AdaptiveLearning/demo_pineline/step7_qlearning/log.txt';

        // Ghi log bước đầu để xem event có chạy không
        file_put_contents($logfile, "\n==== EVENT TRIGGERED ====\n", FILE_APPEND);
        file_put_contents($logfile, json_encode($event, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);

        $valid_components = ['mod_quiz', 'mod_scorm', 'mod_assign', 'mod_forum', 'core', 'mod_resource', 'mod_hvp'];
        // Bỏ qua giáo viên + admin
        if (is_siteadmin($event->userid)) {
            file_put_contents(
                $logfile,
                "SKIP EVENT: User {$event->userid} is site admin → skipped.\n",
                FILE_APPEND
            );
            return;
        }

        if (has_capability(
                'moodle/course:manageactivities',
                \context_course::instance($event->courseid),
                $event->userid
            )) {

            file_put_contents(
                $logfile,
                "SKIP EVENT: User {$event->userid} has manageactivities capability → skipped.\n",
                FILE_APPEND
            );
            return;
        }
        
        if (!in_array($event->component, $valid_components)) {
            file_put_contents(
                $logfile,
                "SKIP EVENT: Component {$event->component} not in valid components → skipped.\n",
                FILE_APPEND
            );
            return;
        }

        $log_data = [
            'userid'           => $event->userid,
            'courseid'         => $event->courseid,
            'eventname'        => $event->eventname,
            'component'        => $event->component,
            'action'           => $event->action,
            'target'           => $event->target,
            'objectid'         => $event->objectid ?? null,
            'crud'             => $event->crud,
            'edulevel'         => $event->edulevel,
            'contextinstanceid'=> $event->contextinstanceid,
            'timecreated'      => $event->timecreated,
            'grade'            => $event->other['grade'] ?? null,
            'success'          => $event->other['success'] ?? null,
        ];

        // Log data gửi đi
        file_put_contents($logfile, "Prepared log_data:\n" . json_encode($log_data, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);

        self::send_to_recommendation_engine([$log_data], $logfile);
    }

    private static function send_to_recommendation_engine($logs, $logfile) {
        $url = 'http://recommend-service:8088/webhook/moodle-events';
        $event_id = uniqid('moodle_event_', true);

        $payload = [
            'logs' => $logs,
            'event_id' => $event_id,
            'timestamp' => time()
        ];

        $data = json_encode($payload);

        // Log payload trước khi gửi
        file_put_contents($logfile, "Sending payload:\n$data\n", FILE_APPEND);

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5); 

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        // Ghi log response
        file_put_contents(
            $logfile,
            "Webhook response: HTTP $http_code\n$response\n-----------------------------\n",
            FILE_APPEND
        );

        // Log thêm khi lỗi
        if ($http_code !== 200 && $http_code !== 202) {
            file_put_contents($logfile, "⚠️ Webhook failed\n", FILE_APPEND);
        }

        curl_close($ch);
    }
}