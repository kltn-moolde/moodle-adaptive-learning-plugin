#!/bin/bash
# Build and push all Docker images to Docker Hub

set -e

# Check if DOCKER_USERNAME is set
if [ -z "$DOCKER_USERNAME" ]; then
    echo "Please set DOCKER_USERNAME environment variable"
    echo "export DOCKER_USERNAME=your-dockerhub-username"
    exit 1
fi

echo "🐳 Building and pushing Docker images for $DOCKER_USERNAME..."

# Build User Service
echo "📦 Building User Service..."
cd userservice
./mvnw clean package -DskipTests
docker build -t $DOCKER_USERNAME/adaptive-learning-user-service:latest .
docker push $DOCKER_USERNAME/adaptive-learning-user-service:latest
cd ..

# Build LTI Service
echo "📦 Building LTI Service..."
cd lti-service-python
docker build -t $DOCKER_USERNAME/adaptive-learning-lti-service:latest .
docker push $DOCKER_USERNAME/adaptive-learning-lti-service:latest
cd ..

# Build Frontend Service
echo "📦 Building Frontend Service..."
cd FE-service-v2
docker build -t $DOCKER_USERNAME/adaptive-learning-frontend:latest .
docker push $DOCKER_USERNAME/adaptive-learning-frontend:latest
cd ..

echo "✅ All images built and pushed successfully!"
echo "🔗 Images available:"
echo "   - $DOCKER_USERNAME/adaptive-learning-user-service:latest"
echo "   - $DOCKER_USERNAME/adaptive-learning-lti-service:latest"
echo "   - $DOCKER_USERNAME/adaptive-learning-frontend:latest"