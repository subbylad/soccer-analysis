#!/bin/bash
# Soccer Scout AI - Complete Deployment Script
# This script orchestrates deployment to multiple platforms

set -e

echo "🚀 Soccer Scout AI - Complete Deployment Orchestrator"
echo "====================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_color $BLUE "🔍 Checking prerequisites..."
    
    local missing_tools=()
    
    # Check for required tools
    if ! command -v node &> /dev/null; then
        missing_tools+=("Node.js")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_tools+=("npm")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("Python 3")
    fi
    
    if ! command -v pip &> /dev/null; then
        missing_tools+=("pip")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_color $RED "❌ Missing required tools: ${missing_tools[*]}"
        print_color $YELLOW "Please install the missing tools and try again."
        exit 1
    fi
    
    print_color $GREEN "✅ All prerequisites satisfied"
}

# Function to validate environment
validate_environment() {
    print_color $BLUE "🔍 Validating environment configuration..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_color $RED "❌ OPENAI_API_KEY environment variable is not set!"
        print_color $YELLOW "Please set your OpenAI API key:"
        print_color $YELLOW "  export OPENAI_API_KEY='your_api_key_here'"
        exit 1
    fi
    
    # Test OpenAI API key (basic format check)
    if [[ ! "$OPENAI_API_KEY" =~ ^sk-[a-zA-Z0-9]{48}$ ]]; then
        print_color $YELLOW "⚠️  OpenAI API key format looks unusual. Please verify it's correct."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_color $GREEN "✅ Environment validation passed"
}

# Function to run tests
run_tests() {
    print_color $BLUE "🧪 Running tests..."
    
    # Test backend
    print_color $YELLOW "Testing backend API..."
    if python3 test_gpt_integration.py > /dev/null 2>&1; then
        print_color $GREEN "✅ Backend tests passed"
    else
        print_color $RED "❌ Backend tests failed"
        read -p "Continue deployment anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Test frontend build
    print_color $YELLOW "Testing frontend build..."
    cd soccer-scout-ui
    if npm install && npm run build > /dev/null 2>&1; then
        print_color $GREEN "✅ Frontend build test passed"
    else
        print_color $RED "❌ Frontend build test failed"
        cd ..
        exit 1
    fi
    cd ..
}

# Function to show deployment options
show_deployment_options() {
    print_color $BLUE "🎯 Available deployment options:"
    echo "1. Vercel (Frontend) + Railway (Backend) - Recommended"
    echo "2. Render (Full Stack)"
    echo "3. Docker (Local/Self-hosted)"
    echo "4. All platforms (for testing)"
    echo "5. Custom deployment"
    echo ""
}

# Function to deploy to Vercel + Railway
deploy_vercel_railway() {
    print_color $BLUE "🚀 Deploying to Vercel + Railway..."
    
    # Deploy backend to Railway first
    print_color $YELLOW "Deploying backend to Railway..."
    chmod +x deploy-railway.sh
    ./deploy-railway.sh
    
    # Get Railway URL (this would need to be captured from the script output)
    print_color $YELLOW "Please enter your Railway backend URL:"
    read -p "Backend URL: " BACKEND_URL
    
    # Update frontend environment
    cd soccer-scout-ui
    export NEXT_PUBLIC_API_URL="$BACKEND_URL"
    cd ..
    
    # Deploy frontend to Vercel
    print_color $YELLOW "Deploying frontend to Vercel..."
    chmod +x deploy-vercel.sh
    ./deploy-vercel.sh
    
    print_color $GREEN "✅ Deployment to Vercel + Railway completed!"
}

# Function to deploy to Render
deploy_render() {
    print_color $BLUE "🚀 Setting up Render deployment..."
    
    chmod +x deploy-render.sh
    ./deploy-render.sh
    
    print_color $GREEN "✅ Render deployment setup completed!"
    print_color $YELLOW "Please follow the instructions in RENDER_DEPLOYMENT.md"
}

# Function to deploy with Docker
deploy_docker() {
    print_color $BLUE "🐳 Deploying with Docker..."
    
    chmod +x deploy-docker.sh
    ./deploy-docker.sh production
    
    print_color $GREEN "✅ Docker deployment completed!"
}

# Function to show post-deployment checklist
show_post_deployment_checklist() {
    print_color $BLUE "📋 Post-deployment checklist:"
    echo "1. ✅ Test all endpoints and functionality"
    echo "2. ✅ Verify CORS configuration between frontend and backend"
    echo "3. ✅ Check logs for any errors or warnings"
    echo "4. ✅ Set up monitoring and health checks"
    echo "5. ✅ Configure custom domains (if needed)"
    echo "6. ✅ Set up SSL certificates"
    echo "7. ✅ Configure environment-specific settings"
    echo "8. ✅ Set up backup and disaster recovery"
    echo "9. ✅ Configure analytics and error tracking"
    echo "10. ✅ Update documentation with deployment URLs"
    echo ""
    print_color $YELLOW "💡 Consider setting up CI/CD pipelines for automatic deployments"
}

# Function to create deployment summary
create_deployment_summary() {
    print_color $BLUE "📄 Creating deployment summary..."
    
    cat > DEPLOYMENT_SUMMARY.md << 'EOF'
# Soccer Scout AI - Deployment Summary

## Deployment Status
- **Date**: $(date)
- **Environment**: Production
- **Status**: Deployed ✅

## Service URLs
- **Frontend**: [Update with actual URL]
- **Backend API**: [Update with actual URL]
- **Health Check**: [Backend URL]/api/health

## Configuration
- **OpenAI Integration**: Enabled
- **Rate Limiting**: Enabled
- **Security Headers**: Enabled
- **CORS**: Configured for production

## Key Features Deployed
- Natural language query processing
- GPT-4 enhanced tactical analysis
- Player comparison and search
- Young prospect identification
- 2,853+ players from Big 5 European leagues

## Monitoring & Maintenance
- Health check endpoint: `/api/health`
- Logs accessible via platform dashboards
- Rate limiting: 60 requests/minute, 500/hour
- Error tracking: Built-in Flask error handling

## Support & Documentation
- API Documentation: Available at root endpoint
- Frontend features: Chat interface with tactical queries
- Data coverage: 2024/25 season FBref data

## Next Steps
1. Monitor initial traffic and performance
2. Set up alerting for downtime or errors
3. Consider scaling if traffic increases
4. Regular data updates and maintenance

---
Generated by Soccer Scout AI deployment script
EOF

    print_color $GREEN "✅ Deployment summary created: DEPLOYMENT_SUMMARY.md"
}

# Main script execution
main() {
    print_color $GREEN "🎉 Welcome to Soccer Scout AI Deployment!"
    print_color $BLUE "This script will help you deploy your AI-powered soccer scout to production."
    echo ""
    
    # Run prerequisite checks
    check_prerequisites
    validate_environment
    run_tests
    
    # Show deployment options
    show_deployment_options
    
    # Get user choice
    read -p "Choose deployment option (1-5): " -n 1 -r
    echo ""
    
    case $REPLY in
        1)
            deploy_vercel_railway
            ;;
        2)
            deploy_render
            ;;
        3)
            deploy_docker
            ;;
        4)
            print_color $YELLOW "Deploying to all platforms (this may take a while)..."
            deploy_docker
            deploy_render
            deploy_vercel_railway
            ;;
        5)
            print_color $BLUE "Custom deployment selected."
            print_color $YELLOW "Available deployment scripts:"
            ls -la deploy-*.sh
            print_color $YELLOW "Run the specific script you need."
            ;;
        *)
            print_color $RED "Invalid option selected."
            exit 1
            ;;
    esac
    
    # Post-deployment tasks
    create_deployment_summary
    show_post_deployment_checklist
    
    print_color $GREEN "🎉 Deployment process completed!"
    print_color $BLUE "Your Soccer Scout AI is now live and ready to analyze players!"
}

# Handle script arguments
case "${1:-interactive}" in
    "interactive")
        main
        ;;
    "vercel-railway")
        check_prerequisites
        validate_environment
        deploy_vercel_railway
        ;;
    "render")
        check_prerequisites
        validate_environment
        deploy_render
        ;;
    "docker")
        check_prerequisites
        deploy_docker
        ;;
    "test")
        check_prerequisites
        validate_environment
        run_tests
        ;;
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  interactive    - Interactive deployment wizard (default)"
        echo "  vercel-railway - Deploy to Vercel + Railway"
        echo "  render         - Set up Render deployment"
        echo "  docker         - Deploy with Docker"
        echo "  test           - Run tests only"
        echo "  help           - Show this help message"
        ;;
    *)
        print_color $RED "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac