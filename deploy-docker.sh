#!/bin/bash
# Soccer Scout AI - Docker Deployment Script
# This script builds and runs the complete application using Docker

set -e

echo "🐳 Soccer Scout AI - Docker Deployment Script"
echo "=============================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info &> /dev/null; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Function to set environment variables
setup_environment() {
    if [ ! -f ".env" ]; then
        echo "⚙️  Setting up environment variables..."
        cp .env.example .env
        echo "📝 Please edit .env file with your OpenAI API key and other settings"
        read -p "Do you want to edit .env now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo "✅ Environment file found"
    fi
}

# Function to build images
build_images() {
    echo "🔨 Building Docker images..."
    
    # Build backend
    echo "Building backend API..."
    docker build -t soccer-scout-api .
    
    # Build frontend (development version)
    echo "Building frontend..."
    cd soccer-scout-ui
    docker build -f Dockerfile.dev -t soccer-scout-frontend .
    cd ..
    
    echo "✅ Docker images built successfully"
}

# Function to run the application
run_application() {
    echo "🚀 Starting Soccer Scout AI..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    # Start services
    $COMPOSE_CMD up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if $COMPOSE_CMD ps | grep -q "Up"; then
        echo "✅ Services started successfully!"
        echo ""
        echo "🌐 Application URLs:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend API: http://localhost:5001"
        echo "   Health Check: http://localhost:5001/api/health"
        echo ""
        echo "📊 Check status with: $COMPOSE_CMD ps"
        echo "📋 View logs with: $COMPOSE_CMD logs -f"
    else
        echo "❌ Failed to start services. Check logs:"
        $COMPOSE_CMD logs
        exit 1
    fi
}

# Function to run production build
run_production() {
    echo "🏭 Running production build..."
    
    # Build production frontend
    cd soccer-scout-ui
    docker build -t soccer-scout-frontend-prod .
    cd ..
    
    # Create production docker-compose
    cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  api:
    image: soccer-scout-api
    container_name: soccer-scout-api-prod
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - NODE_ENV=production
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5001/api/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: soccer-scout-frontend-prod
    container_name: soccer-scout-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://localhost:5001
    restart: unless-stopped

networks:
  default:
    name: soccer-scout-prod
EOF
    
    # Start production services
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.prod.yml up -d
    else
        docker compose -f docker-compose.prod.yml up -d
    fi
    
    echo "✅ Production deployment started!"
}

# Function to stop the application
stop_application() {
    echo "🛑 Stopping Soccer Scout AI..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    echo "✅ Application stopped"
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up Docker resources..."
    
    # Stop containers
    docker stop soccer-scout-api soccer-scout-frontend 2>/dev/null || true
    
    # Remove containers
    docker rm soccer-scout-api soccer-scout-frontend 2>/dev/null || true
    
    # Remove images (optional)
    read -p "Do you want to remove Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi soccer-scout-api soccer-scout-frontend 2>/dev/null || true
        echo "✅ Docker images removed"
    fi
    
    echo "✅ Cleanup completed"
}

# Main script logic
case "${1:-run}" in
    "run")
        check_docker
        check_docker_compose
        setup_environment
        build_images
        run_application
        ;;
    "production")
        check_docker
        check_docker_compose
        setup_environment
        build_images
        run_production
        ;;
    "stop")
        stop_application
        ;;
    "cleanup")
        cleanup
        ;;
    "build")
        check_docker
        build_images
        ;;
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  run        - Build and run development environment (default)"
        echo "  production - Build and run production environment"
        echo "  stop       - Stop running containers"
        echo "  cleanup    - Stop and remove containers/images"
        echo "  build      - Build Docker images only"
        echo "  help       - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                  # Run development environment"
        echo "  $0 production       # Run production environment"
        echo "  $0 stop            # Stop all containers"
        echo "  $0 cleanup         # Clean up everything"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac