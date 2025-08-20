package com.example.gatewayservice.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                // LTI Service routes using service discovery
                .route("lti-service", r -> r.path("/lti/**")
                        .uri("lb://lti-service"))
                
                // Recommendation Service routes using service discovery
                .route("recommendation-service", r -> r.path("/api/recommendations/**")
                        .uri("lb://recommendation-service"))
                
                // Course Service routes using service discovery
                .route("course-service", r -> r.path("/api/courses/**")
                        .uri("lb://course-service"))
                
                // Analytics Service routes using service discovery
                .route("analytics-service", r -> r.path("/api/analytics/**")
                        .uri("lb://analytics-service"))
                
                // User Service routes using service discovery
                .route("user-service", r -> r.path("/api/users/**")
                        .uri("lb://user-service"))
                
                // Common Service routes using service discovery
                .route("common-service", r -> r.path("/api/common/**")
                        .uri("lb://common-service"))
                
                // React Frontend (fallback for SPA routing)
                .route("react-frontend", r -> r.path("/**")
                        .and().not(p -> p.path("/api/**"))
                        .and().not(p -> p.path("/lti/**"))
                        .uri("http://localhost:3000"))
                
                .build();
    }

    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration corsConfig = new CorsConfiguration();
        corsConfig.setAllowCredentials(false);
        corsConfig.addAllowedOriginPattern("*");
        corsConfig.addAllowedMethod("*");
        corsConfig.addAllowedHeader("*");

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }
}
