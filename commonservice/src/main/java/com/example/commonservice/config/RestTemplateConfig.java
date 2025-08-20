package com.example.commonservice.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofMillis(3000)) // Thời gian chờ kết nối
                .setReadTimeout(Duration.ofMillis(5000))    // Thời gian chờ đọc dữ liệu
                .build();
    }
}