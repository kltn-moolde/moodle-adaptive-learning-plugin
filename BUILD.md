# Build and Push Scripts for Development

## Quick Build and Push All Services

```bash
# Set your Docker Hub username
export DOCKER_USERNAME=your-dockerhub-username

# Build and push all services
./scripts/build-and-push.sh
```

## Individual Service Scripts

### User Service
```bash
cd userservice
./mvnw clean package -DskipTests
docker build -t $DOCKER_USERNAME/adaptive-learning-user-service:latest .
docker push $DOCKER_USERNAME/adaptive-learning-user-service:latest
```

### LTI Service  
```bash
cd lti-service-python
docker build -t $DOCKER_USERNAME/adaptive-learning-lti-service:latest .
docker push $DOCKER_USERNAME/adaptive-learning-lti-service:latest
```

### Frontend Service
```bash
cd FE-service-v2
docker build -t $DOCKER_USERNAME/adaptive-learning-frontend:latest .
docker push $DOCKER_USERNAME/adaptive-learning-frontend:latest
```

## Local Testing

```bash
# Test locally with production images
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Clean up
docker-compose -f docker-compose.prod.yml down
```