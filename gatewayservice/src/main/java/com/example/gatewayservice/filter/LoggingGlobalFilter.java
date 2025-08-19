package com.example.gatewayservice.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;

@Component
public class LoggingGlobalFilter implements GlobalFilter, Ordered {

    private static final Logger logger = LoggerFactory.getLogger(LoggingGlobalFilter.class);

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        logger.info("Gateway Request: {} {} at {}",
                request.getMethod(),
                request.getURI(),
                LocalDateTime.now());

        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            logger.info("Gateway Response: {} for {} {}",
                    exchange.getResponse().getStatusCode(),
                    request.getMethod(),
                    request.getURI());
        }));
    }

    @Override
    public int getOrder() {
        return -1; // Execute first
    }
}
