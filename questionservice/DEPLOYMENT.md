# Question Service - Run with Gunicorn

## Development Mode

### Option 1: Direct Python (Development)
```bash
cd questionservice
python3 app.py
```
Service runs on `http://localhost:5003` with auto-reload.

### Option 2: Gunicorn (Production-like)
```bash
cd questionservice
./start.sh
```
Service runs on `http://0.0.0.0:5003` with 4 workers.

## Production Mode

### Gunicorn Command
```bash
gunicorn --bind 0.0.0.0:5003 \
         --workers 4 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --log-level info \
         "app:app"
```

### Parameters Explained
- `--bind 0.0.0.0:5003` - Listen on all interfaces, port 5003
- `--workers 4` - 4 worker processes (adjust based on CPU cores)
- `--timeout 120` - 120 second timeout (for AI requests)
- `--access-logfile` - Log all requests
- `--error-logfile` - Log errors
- `--log-level info` - Info level logging
- `"app:app"` - Module name:app instance

### Worker Calculation
```
workers = (2 × CPU cores) + 1
```
- 2 cores: 5 workers
- 4 cores: 9 workers
- 8 cores: 17 workers

### Background Mode
```bash
# Start in background
gunicorn --bind 0.0.0.0:5003 \
         --workers 4 \
         --timeout 120 \
         --daemon \
         --pid gunicorn.pid \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         "app:app"

# Stop
kill $(cat gunicorn.pid)
```

## Docker

### Build and Run
```bash
docker build -t questionservice .
docker run -d \
  -p 5003:5003 \
  -e MONGO_URI="your_mongodb_uri" \
  -e GEMINI_API_KEY="your_api_key" \
  --name questionservice \
  questionservice
```

### Docker Compose
```bash
docker-compose up -d
```

## Systemd Service (Linux)

Create `/etc/systemd/system/questionservice.service`:
```ini
[Unit]
Description=Question Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/questionservice
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn \
    --bind 0.0.0.0:5003 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/questionservice/access.log \
    --error-logfile /var/log/questionservice/error.log \
    "app:app"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable questionservice
sudo systemctl start questionservice
sudo systemctl status questionservice
```

## Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

## Monitoring

### Check if running
```bash
ps aux | grep gunicorn
```

### Check logs
```bash
tail -f logs/access.log
tail -f logs/error.log
```

### Health check
```bash
curl http://localhost:5003/health
```

### Monitor workers
```bash
watch -n 1 'ps aux | grep gunicorn'
```

## Performance Tips

1. **Workers**: Use `(2 × CPU cores) + 1`
2. **Timeout**: 120s for AI requests
3. **Keep-alive**: Use reverse proxy (Nginx)
4. **Log rotation**: Configure logrotate
5. **Memory**: Monitor with `htop` or `top`

## Troubleshooting

### Port already in use
```bash
# Find process
lsof -i :5003

# Kill process
kill -9 <PID>
```

### Workers timeout
```bash
# Increase timeout
gunicorn --timeout 300 ...
```

### Memory issues
```bash
# Reduce workers
gunicorn --workers 2 ...
```

### Permission denied
```bash
# Check file permissions
chmod +x start.sh

# Check port permissions (< 1024 needs sudo)
sudo gunicorn --bind 0.0.0.0:80 ...
```

## Quick Commands

```bash
# Development
python3 app.py

# Production (foreground)
gunicorn --bind 0.0.0.0:5003 --workers 4 --timeout 120 "app:app"

# Production (background)
./start.sh &

# Docker
docker-compose up -d

# Check status
curl http://localhost:5003/health

# View logs
tail -f logs/error.log
```

## Comparison

| Mode | Use Case | Auto-reload | Workers | Performance |
|------|----------|-------------|---------|-------------|
| `python3 app.py` | Development | ✅ Yes | 1 | Low |
| `gunicorn` | Production | ❌ No | Multiple | High |
| Docker | Production | ❌ No | Multiple | High |

---

**Recommended**: Use Gunicorn for production, direct Python for development.
