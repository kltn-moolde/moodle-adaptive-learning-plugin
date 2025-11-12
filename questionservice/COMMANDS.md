# Question Service - Management Commands

## Quick Commands

```bash
# Start service
./start.sh

# Stop service
./stop.sh

# Restart service
./restart.sh

# Check status
./status.sh
```

## Development vs Production

### Development Mode
```bash
# Direct Python - auto-reload on code changes
python3 app.py
```
- Auto-reload when code changes
- Debug mode enabled
- Single process
- Use for: Development, testing

### Production Mode
```bash
# Gunicorn - multiple workers
./start.sh
```
- Multiple workers for concurrency
- No auto-reload
- Production-ready
- Use for: Staging, production

## Service Management

### Start
```bash
# Basic start
./start.sh

# Custom configuration
gunicorn -c gunicorn.conf.py app:app

# With specific workers
gunicorn --bind 0.0.0.0:5003 --workers 8 --timeout 120 app:app
```

### Stop
```bash
# Graceful stop
./stop.sh

# Force stop all
pkill -f "gunicorn.*app:app"
```

### Restart
```bash
# Stop and start
./restart.sh

# Reload workers (zero downtime)
kill -HUP $(cat gunicorn.pid)
```

### Status
```bash
# Check status
./status.sh

# Check processes
ps aux | grep gunicorn

# Check port
lsof -i :5003
```

## Monitoring

### View Logs
```bash
# Follow error log
tail -f logs/error.log

# Follow access log
tail -f logs/access.log

# View recent errors
tail -50 logs/error.log

# Search logs
grep "ERROR" logs/error.log
```

### Health Check
```bash
# Quick check
curl http://localhost:5003/health

# Formatted
curl -s http://localhost:5003/health | python3 -m json.tool

# With monitoring
watch -n 5 'curl -s http://localhost:5003/health'
```

### Statistics
```bash
# Question statistics
curl -s http://localhost:5003/api/questions/statistics | python3 -m json.tool
```

### System Monitoring
```bash
# CPU and Memory usage
htop

# Watch processes
watch -n 2 'ps aux | grep gunicorn'

# Network connections
netstat -an | grep :5003
```

## Configuration

### Using gunicorn.conf.py
```bash
# Start with config file
gunicorn -c gunicorn.conf.py app:app
```

### Environment Variables
```bash
# Set before starting
export MONGO_URI="mongodb://..."
export GEMINI_API_KEY="your_key"
./start.sh

# Or inline
MONGO_URI="mongodb://..." ./start.sh
```

### Custom Workers
```bash
# Based on CPU cores
WORKERS=$(($(nproc) * 2 + 1))
gunicorn --workers $WORKERS app:app
```

## Troubleshooting

### Service won't start
```bash
# Check if port is in use
lsof -i :5003

# Check logs
cat logs/error.log

# Try different port
gunicorn --bind 0.0.0.0:5004 app:app
```

### High memory usage
```bash
# Reduce workers
gunicorn --workers 2 app:app

# Enable max_requests
gunicorn --max-requests 1000 app:app
```

### Timeout errors
```bash
# Increase timeout
gunicorn --timeout 300 app:app
```

### Workers dying
```bash
# Check error log
tail -f logs/error.log

# Increase timeout and memory
gunicorn --timeout 300 --worker-tmp-dir /dev/shm app:app
```

## Load Testing

### ApacheBench
```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5003/health
```

### wrk
```bash
# 30 seconds, 10 threads, 100 connections
wrk -t10 -c100 -d30s http://localhost:5003/health
```

## Backup and Maintenance

### Backup logs
```bash
# Compress old logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/*.log

# Clean old logs
> logs/access.log
> logs/error.log
```

### Update service
```bash
# Stop service
./stop.sh

# Pull latest code
git pull

# Install dependencies
pip install -r requirements.txt

# Start service
./start.sh
```

## Production Checklist

- [ ] Environment variables configured
- [ ] MongoDB connection tested
- [ ] Gemini API key valid
- [ ] Logs directory created
- [ ] Port 5003 available
- [ ] Firewall configured (if needed)
- [ ] Nginx reverse proxy (optional)
- [ ] SSL certificate (optional)
- [ ] Monitoring setup
- [ ] Backup strategy defined

## Systemd Integration (Linux)

### Create service file
```bash
sudo nano /etc/systemd/system/questionservice.service
```

### Manage with systemd
```bash
# Start
sudo systemctl start questionservice

# Stop
sudo systemctl stop questionservice

# Restart
sudo systemctl restart questionservice

# Status
sudo systemctl status questionservice

# Enable on boot
sudo systemctl enable questionservice

# View logs
sudo journalctl -u questionservice -f
```

## Nginx Reverse Proxy

### Basic configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
```

### Test Nginx
```bash
# Test configuration
sudo nginx -t

# Reload
sudo nginx -s reload
```

## Performance Tuning

### Optimal workers
```bash
# Formula: (2 × CPU cores) + 1
workers = (2 × cores) + 1

# Example for 4 cores
gunicorn --workers 9 app:app
```

### Worker class
```bash
# Sync (default) - for CPU-bound
gunicorn --worker-class sync app:app

# Gevent - for I/O-bound
gunicorn --worker-class gevent --worker-connections 1000 app:app
```

### Memory management
```bash
# Restart workers after N requests
gunicorn --max-requests 1000 --max-requests-jitter 50 app:app
```

---

**Recommended Commands**:
- Development: `python3 app.py`
- Production: `./start.sh`
- Status: `./status.sh`
- Logs: `tail -f logs/error.log`
