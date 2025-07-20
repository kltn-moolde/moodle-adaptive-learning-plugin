package com.example.plugin_moodle_LTI_13.service;

import com.example.plugin_moodle_LTI_13.model.MoodleApiResponse;
import com.example.plugin_moodle_LTI_13.model.UserLog;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import reactor.core.publisher.Mono;
import java.util.List;
import java.util.Collections;

@Service
public class MoodleApiService {

    private final WebClient webClient;

    @Value("${moodle.api.url}")
    private String moodleApiUrl;

    @Value("${moodle.api.token}")
    private String moodleApiToken;


    public MoodleApiService() {
        this.webClient = WebClient.builder().build();
    }

    public MoodleApiService(WebClient webClient) {
        this.webClient = webClient;
    }

    public List<UserLog> getUserLogs(String courseId) {  // Kiet chạy duọc
        try {
            MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
            params.add("wstoken", moodleApiToken);
            params.add("wsfunction", "local_userlog_get_module_logs");
            params.add("moodlewsrestformat", "json");
            params.add("cmid", courseId);

            System.out.println("Final API URL: " + moodleApiUrl);
            System.out.println("Parameters: " + params);

            // Parse array of UserLog
            List<UserLog> logs = webClient
                    .post()
                    .uri(moodleApiUrl)
                    .bodyValue(params)
                    .retrieve()
                    .bodyToFlux(UserLog.class) // parse từng object trong array
                    .collectList()             // gom thành List<UserLog>
                    .block();                  // chờ kết quả

            return logs != null ? logs : Collections.emptyList();

        } catch (Exception e) {
            System.err.println("Error calling Moodle API: " + e.getMessage());
            return Collections.emptyList();
        }
    }

//    public List<UserLog> getUserLogs(int cmid) { // Loc chạy
//        try {
//
//            MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
//            params.add("wstoken", moodleApiToken);
//            params.add("wsfunction", "local_userlog_get_module_logs");
//            params.add("moodlewsrestformat", "json");
//            params.add("cmid", String.valueOf(cmid));
//
//
//            String url = String.format(
//                    "http://localhost:8100/webservice/rest/server.php?wstoken=%s&wsfunction=%s&moodlewsrestformat=json&cmid=%d",
//                    moodleApiToken,
//                    "local_userlog_get_module_logs",
//                    cmid
//            );
//
//            System.out.println("Final API URL: " + url);
//
//            List<UserLog> logs = webClient
//                    .get()
//                    .uri(url)
//                    .retrieve()
//                    .bodyToFlux(UserLog.class)
//                    .collectList()
//                    .block();
//
//            return logs != null ? logs : Collections.emptyList();
//
//        } catch (Exception e) {
//            System.err.println("❌ Error calling Moodle API: " + e.getMessage());
//            return Collections.emptyList();
//        }
//    }


//    public List<UserLog> getUserLogsByUser(String courseId, String userId) {
//        try {
//            MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
//            params.add("wstoken", moodleApiToken);
//            params.add("wsfunction", "local_userlog_get_module_logs");
//            params.add("moodlewsrestformat", "json");
//            params.add("idcourse", courseId);
//            params.add("userid", userId);
//
//            Mono<MoodleApiResponse> responseMono = webClient
//                    .post()
//                    .uri(moodleApiUrl)
//                    .bodyValue(params)
//                    .retrieve()
//                    .bodyToMono(MoodleApiResponse.class);
//
//            MoodleApiResponse response = responseMono.block();
//
//            if (response != null && response.getLogs() != null) {
//                return response.getLogs();
//            }
//
//            return Collections.emptyList();
//
//        } catch (Exception e) {
//            System.err.println("Error calling Moodle API: " + e.getMessage());
//            return Collections.emptyList();
//        }
//    }
}