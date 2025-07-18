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

    public List<UserLog> getUserLogs(String courseId) {
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


    public List<UserLog> getUserLogsByUser(String courseId, String userId) {
        try {
            MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
            params.add("wstoken", moodleApiToken);
            params.add("wsfunction", "local_userlog_get_module_logs");
            params.add("moodlewsrestformat", "json");
            params.add("idcourse", courseId);
            params.add("userid", userId);

            Mono<MoodleApiResponse> responseMono = webClient
                    .post()
                    .uri(moodleApiUrl)
                    .bodyValue(params)
                    .retrieve()
                    .bodyToMono(MoodleApiResponse.class);

            MoodleApiResponse response = responseMono.block();

            if (response != null && response.getLogs() != null) {
                return response.getLogs();
            }

            return Collections.emptyList();

        } catch (Exception e) {
            System.err.println("Error calling Moodle API: " + e.getMessage());
            return Collections.emptyList();
        }
    }
}