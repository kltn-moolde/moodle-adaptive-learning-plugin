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
                // LTI Service routes
                .route("lti-service", r -> r.path("/lti/**")
                        .uri("http://localhost:8082"))
                
                // Recommendation Service routes
                .route("recommendation-service", r -> r.path("/api/recommendations/**")
                        .uri("http://localhost:8083"))
                
                // Course Service routes
                .route("course-service", r -> r.path("/api/courses/**")
                        .uri("http://localhost:8084"))
                
                // Analytics Service routes
                .route("analytics-service", r -> r.path("/api/analytics/**")
                        .uri("http://localhost:8085"))
                
                // User Service routes
                .route("user-service", r -> r.path("/api/users/**")
                        .uri("http://localhost:8086"))
                
                // React Frontend (fallback for SPA routing)
                .route("react-frontend", r -> r.path("/**")
                        .and().not(path -> path.getPath().startsWith("/api/") || 
                                          path.getPath().startsWith("/lti/"))
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
