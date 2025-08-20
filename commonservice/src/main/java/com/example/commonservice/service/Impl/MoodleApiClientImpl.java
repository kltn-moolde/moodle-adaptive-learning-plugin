package com.example.commonservice.service.Impl;

import com.example.commonservice.enums.TokenType;
import com.example.commonservice.service.MoodleApiClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

@Service
public class MoodleApiClientImpl implements MoodleApiClient {

    private final RestTemplate restTemplate;

    @Value("${moodle.api.url}")
    private String moodleUrl;

    @Value("${moodle.api.token-plugin}")
    private String apiTokenPlugin;

    @Value("${moodle.api.token-system}")
    private String apiTokenSystem;

    public MoodleApiClientImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

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

        try {
            ResponseEntity<T> response = restTemplate.exchange(
                    uriBuilder.toUriString(),
                    HttpMethod.GET,
                    null,
                    responseType
            );
            return response.getBody();
        } catch (Exception e) {
            throw new Exception("Lỗi khi gọi Moodle API: " + e.getMessage(), e);
        }
    }


    /**
     * ============================
     * 💡 CÁCH SỬ DỤNG (HƯỚNG DẪN) 💡
     * ============================
     *
     * 👉 1. Gọi API KHÔNG CẦN PARAMS (ví dụ lấy thông tin site):
     *
     * var siteInfo = moodleApiClient.callMoodleApi(
     *      "core_webservice_get_site_info",
     *      null,                        // không cần params
     *      SiteInfoResponse.class,
     *      TokenType.SYSTEM
     * );
     *
     * 👉 2. Gọi API CÓ PARAMS DẠNG criteria[] (tìm user theo email / username):
     *
     * var users = moodleApiClient.callMoodleApi(
     *      "core_user_get_users",
     *      MoodleParams.create()
     *          .criteria("email", "test@test.com")
     *          .criteria("username", "john")
     *          .build(),
     *      UserResponse.class,
     *      TokenType.SYSTEM
     * );
     *
     * 👉 3. Gọi API PLUGIN CUSTOM (ví dụ local_myplugin_get_data):
     *
     * var pluginData = moodleApiClient.callMoodleApi(
     *      "local_myplugin_get_data",
     *      MoodleParams.create()
     *          .add("userid", 5)
     *          .add("courseid", 101)
     *          .build(),
     *      MyPluginResponse.class,
     *      TokenType.PLUGIN
     * );
     *
     * 👉 4. Nếu API có nhiều criteria (search nâng cao):
     *
     * MoodleParams.create()
     *      .criteria("email", "a@b.com")
     *      .criteria("idnumber", "12345")
     *      .criteria("username", "loc")
     *      .build();
     *
     */
}