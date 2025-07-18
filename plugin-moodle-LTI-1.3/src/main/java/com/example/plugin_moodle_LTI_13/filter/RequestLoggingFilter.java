package com.example.plugin_moodle_LTI_13.filter;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Arrays;

@Component
public class RequestLoggingFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;

        System.out.println("=== FILTER DEBUG ===");
        System.out.println("Method: " + httpRequest.getMethod());
        System.out.println("URI: " + httpRequest.getRequestURI());
        System.out.println("Query String: " + httpRequest.getQueryString());

        // Log all parameters
        System.out.println("Parameters:");
        httpRequest.getParameterMap().forEach((key, values) -> {
            System.out.println("  " + key + " = " + Arrays.toString(values));
        });

        try {
            chain.doFilter(request, response);
        } catch (Exception e) {
            System.err.println("ERROR in filter: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }
}
