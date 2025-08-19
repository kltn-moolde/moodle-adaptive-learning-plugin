package com.example.plugin_moodle_LTI_13.config;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;


import java.util.Arrays;
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Value("${lti.tool.issuer}")
    private String issuer;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .headers(headers -> headers
                        .addHeaderWriter((request, response) -> {
                            response.setHeader("X-Frame-Options", "ALLOWALL");
                        })
                )
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/lti/login", "/lti/launch", "/error", "lti/dashboard", "lti/logs", "/lti/api/logs", "lti/config", "lti/jwks").permitAll()
                        .anyRequest().authenticated()
                )
                .csrf(csrf -> csrf.disable())
                .cors(cors -> cors.configurationSource(request -> {
                    CorsConfiguration config = new CorsConfiguration();
                    config.setAllowedOrigins(Arrays.asList(issuer)); // Cho phép Moodle
                    config.setAllowedMethods(Arrays.asList("GET", "POST"));
                    config.setAllowedHeaders(Arrays.asList("*"));
                    return config;
                }));

        return http.build();
    }
}