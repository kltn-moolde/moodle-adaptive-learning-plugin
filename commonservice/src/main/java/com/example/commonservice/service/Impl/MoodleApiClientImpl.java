package com.example.commonservice.service.Impl;

import com.example.commonservice.enums.TokenType;
import com.example.commonservice.service.MoodleApiClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.CloseableHttpResponse;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.HttpEntity;
import org.apache.hc.core5.http.io.entity.EntityUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class MoodleApiClientImpl implements MoodleApiClient {

    private final ObjectMapper objectMapper = new ObjectMapper(); // để parse JSON

    @Value("${moodle.api.url}")
    private String moodleUrl;

    @Value("${moodle.api.token-plugin}")
    private String apiTokenPlugin;

    @Value("${moodle.api.token-system}")
    private String apiTokenSystem;

    @Override
    public <T> T callMoodleApi(String wsfunction, Map<String, Object> params, Class<T> responseType, TokenType tokenType) throws Exception {
        String tokenToUse = (tokenType == TokenType.SYSTEM) ? apiTokenSystem : apiTokenPlugin;

        UriComponentsBuilder uriBuilder = UriComponentsBuilder.fromHttpUrl(moodleUrl)
                .queryParam("wstoken", tokenToUse)
                .queryParam("wsfunction", wsfunction)
                .queryParam("moodlewsrestformat", "json");

        if (params != null) {
            params.forEach(uriBuilder::queryParam);
        }

        String finalUrl = uriBuilder.toUriString();
        System.out.println("🔎 Moodle API URL (HttpClient): " + finalUrl);

        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpGet request = new HttpGet(finalUrl);

            try (CloseableHttpResponse response = httpClient.execute(request)) {
                int statusCode = response.getCode();
                if (statusCode != 200) {
                    throw new Exception("Moodle API trả về lỗi HTTP: " + statusCode);
                }

                HttpEntity entity = response.getEntity();
                if (entity == null) {
                    throw new Exception("Moodle API không trả dữ liệu");
                }

                String result = EntityUtils.toString(entity);

                // parse JSON sang object mong muốn
                return objectMapper.readValue(result, responseType);
            }
        } catch (Exception e) {
            throw new Exception("Lỗi khi gọi Moodle API bằng HttpClient: " + e.getMessage(), e);
        }
    }
}


//// 🔎 Lấy danh sách user theo email
//var users = moodleApiClient.callMoodleApi(
//        "core_user_get_users",
//        MoodleParams.create()
//                .criteria("email", "test@test.com")
//                .criteria("username", "loc")   // có thể add nhiều tiêu chí
//                .build(),
//        UserResponse.class,
//        TokenType.SYSTEM
//);
//
//// 🔎 Lấy thông tin course
//var courses = moodleApiClient.callMoodleApi(
//        "core_course_get_courses",
//        null,   // không cần params
//        CourseResponse[].class,
//        TokenType.SYSTEM
//);