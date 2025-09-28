# Stage 1: build
FROM node:22-bullseye AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (dev + prod)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build -- --mode production

# Stage 2: production
FROM node:22-bullseye
WORKDIR /app

# Install serve to serve static files
RUN npm install -g serve

# Create group & user
RUN groupadd -g 1001 frontend \
    && useradd -m -u 1001 -g frontend frontend


# Copy built app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# Install only production dependencies
RUN npm ci --only=production && npm cache clean --force

# Change ownership to frontend user
RUN chown -R frontend:frontend /app
USER frontend

# Expose port (serve default)
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5173 || exit 1

# Start the application
CMD ["serve", "-s", "dist", "-l", "5173"]
