FROM nginx:alpine

# Install additional tools
RUN apk add --no-cache curl

# Copy NGINX configuration
COPY conf/ /etc/nginx/conf.d/
COPY conf/nginx.conf /etc/nginx/nginx.conf

# Create log directory
RUN mkdir -p /var/log/nginx

# Create custom error pages
RUN mkdir -p /usr/share/nginx/html/errors

# Copy custom error pages
COPY errors/ /usr/share/nginx/html/errors/

# Set proper permissions
RUN chown -R nginx:nginx /var/log/nginx
RUN chown -R nginx:nginx /etc/nginx
RUN chown -R nginx:nginx /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
