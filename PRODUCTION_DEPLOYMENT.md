# Production Deployment Guide

This guide covers deploying the Smartphone Intelligence Platform API to production using Gunicorn with Uvicorn workers.

## Prerequisites

- Python 3.13+
- All dependencies installed (`pip install -r requirements.txt`)
- Snowflake credentials configured
- Production server (Linux recommended)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your production values:

```bash
cp .env.example .env
# Edit .env with your production credentials
```

**Important:** In production, prefer using:
- Environment variables set by your deployment system
- Secrets management services (AWS Secrets Manager, HashiCorp Vault, etc.)
- Kubernetes Secrets
- Docker secrets

### 3. Run with Gunicorn

```bash
gunicorn backend.main:app -c gunicorn.conf.py
```

Or specify configuration inline:

```bash
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | API server port | `8000` | No |
| `API_HOST` | Bind address | `0.0.0.0` | No |
| `ENVIRONMENT` | `production` or `development` | `production` | No |
| `GUNICORN_WORKERS` | Number of worker processes | `CPU * 2 + 1` | No |
| `GUNICORN_ACCESS_LOG` | Access log file (`-` for stdout) | `-` | No |
| `GUNICORN_ERROR_LOG` | Error log file (`-` for stderr) | `-` | No |
| `GUNICORN_LOG_LEVEL` | Log level | `info` | No |

### Gunicorn Configuration

The `gunicorn.conf.py` file contains production-ready settings:

- **Workers**: Automatically set to `CPU count * 2 + 1` (optimal for I/O-bound FastAPI)
- **Worker Class**: `uvicorn.workers.UvicornWorker` for async support
- **Timeout**: 60 seconds (adjust based on your query performance)
- **Max Requests**: 1000 (prevents memory leaks by restarting workers)
- **Preload App**: Enabled (faster worker startup)

### Worker Count Calculation

For I/O-bound applications like this API (waiting on Snowflake queries):

```
workers = (CPU cores × 2) + 1
```

Example:
- 2 CPU cores → 5 workers
- 4 CPU cores → 9 workers
- 8 CPU cores → 17 workers

## Health Checks

The API provides multiple health check endpoints:

### `/health`
Comprehensive health check with database status:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "api": "running",
  "version": "1.0.0",
  "timestamp": 1234567890.123,
  "databases": {
    "snowflake": "connected"
  }
}
```

### `/health/live` (Liveness Probe)
Returns 200 if the application process is running:
```bash
curl http://localhost:8000/health/live
```

### `/health/ready` (Readiness Probe)
Returns 200 only if ready to serve traffic (databases connected):
```bash
curl http://localhost:8000/health/ready
```

**Kubernetes Example:**
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Deployment Options

### Option 1: Systemd Service

Create `/etc/systemd/system/smartphone-api.service`:

```ini
[Unit]
Description=Smartphone Intelligence Platform API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/smartphone-intelligence-platform
Environment="PATH=/opt/smartphone-intelligence-platform/.venv/bin"
EnvironmentFile=/opt/smartphone-intelligence-platform/.env
ExecStart=/opt/smartphone-intelligence-platform/.venv/bin/gunicorn backend.main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable smartphone-api
sudo systemctl start smartphone-api
sudo systemctl status smartphone-api
```

### Option 2: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.main:app", "-c", "gunicorn.conf.py"]
```

Build and run:
```bash
docker build -t smartphone-api .
docker run -d \
  --name smartphone-api \
  -p 8000:8000 \
  --env-file .env \
  smartphone-api
```

### Option 3: Kubernetes

See `kubernetes/` directory for example manifests (if created).

### Option 4: Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
upstream smartphone_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://smartphone_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://smartphone_api;
        access_log off;
    }
}
```

## Security Best Practices

### 1. Credentials Management
- ✅ **Never log passwords or credentials**
- ✅ Use environment variables or secrets management
- ✅ Rotate credentials regularly
- ✅ Use least-privilege database access

### 2. Network Security
- ✅ Use HTTPS in production (via reverse proxy or load balancer)
- ✅ Bind to `0.0.0.0` only if behind a firewall/reverse proxy
- ✅ Use firewall rules to restrict access

### 3. Application Security
- ✅ Keep dependencies updated
- ✅ Monitor logs for errors
- ✅ Set appropriate file permissions on `.env`
- ✅ Use non-root user for running the application

### 4. Monitoring
- ✅ Monitor `/health` endpoint
- ✅ Set up log aggregation
- ✅ Monitor Snowflake connection pool
- ✅ Track API response times

## Performance Tuning

### Worker Count
Adjust based on:
- CPU cores available
- Memory available (each worker uses ~50-100MB)
- Expected concurrent requests

### Connection Pool
The API uses a Snowflake connection pool (default: 5 connections). Adjust in `backend/main.py`:

```python
snowflake_pool = SnowflakeConnectionPool(max_connections=10)
```

### Timeouts
- **Gunicorn timeout**: 60 seconds (in `gunicorn.conf.py`)
- **Snowflake timeout**: 60 seconds (in `pipeline/db_snowflake.py`)

Adjust based on your query performance.

## Logging

### Access Logs
Log all HTTP requests:
```bash
GUNICORN_ACCESS_LOG=/var/log/smartphone-api/access.log
```

### Error Logs
Log application errors:
```bash
GUNICORN_ERROR_LOG=/var/log/smartphone-api/error.log
```

### Log Rotation
Use `logrotate` to manage log files:

```
/var/log/smartphone-api/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload smartphone-api > /dev/null 2>&1 || true
    endscript
}
```

## Troubleshooting

### API Not Starting
1. Check environment variables are set correctly
2. Verify Snowflake credentials
3. Check port is not already in use: `netstat -tulpn | grep 8000`
4. Review error logs: `journalctl -u smartphone-api -f`

### Database Connection Issues
1. Verify Snowflake credentials in `.env`
2. Check network connectivity to Snowflake
3. Verify warehouse is running
4. Check `/health` endpoint for detailed error

### High Memory Usage
1. Reduce worker count
2. Enable `max_requests` to restart workers periodically
3. Monitor connection pool size

## Monitoring

### Health Check Monitoring
Set up monitoring to check `/health` endpoint every 30 seconds:

```bash
# Simple monitoring script
while true; do
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "API is down! $(date)"
        # Add alerting here
    fi
    sleep 30
done
```

### Metrics to Monitor
- API response time (p50, p95, p99)
- Error rate
- Snowflake connection pool usage
- Worker process health
- Memory usage per worker

## Support

For issues or questions:
1. Check logs: `journalctl -u smartphone-api -f`
2. Review health endpoint: `curl http://localhost:8000/health`
3. Check Snowflake connection: Review connection pool logs
