# Stage 1: build
FROM node:20-bullseye AS builder
WORKDIR /app

COPY package*.json ./

RUN npm install -g npm@latest
RUN npm ci

COPY . .

RUN npm run build

# Stage 2: production
FROM node:20-bullseye 
WORKDIR /app

RUN npm install -g serve

RUN groupadd -g 1001 frontend \
    && useradd -m -u 1001 -g frontend frontend

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

RUN npm ci --only=production && npm cache clean --force
RUN chown -R frontend:frontend /app
USER frontend

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5173 || exit 1

CMD ["serve", "-s", "dist", "-l", "5173"]