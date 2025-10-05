# Quick Start Guide

## 🚀 Option 1: Using Docker (Recommended)

1. **Start Docker Desktop** (if not already running)

2. **Build and run with one command:**
   \\\ash
   docker-compose up --build
   \\\

3. **Test the API:**
   \\\ash
   curl http://localhost:8000/health
   curl http://localhost:8000/docs
   \\\

## 💻 Option 2: Local Development

1. **Install dependencies:**
   \\\ash
   pip install -r requirements.txt
   \\\

2. **Run the application:**
   \\\ash
   python -m uvicorn app.main:app --reload
   \\\

3. **Test the API:**
   \\\ash
   curl http://127.0.0.1:8000/health
   \\\

## 🔧 Available Commands

- \make help\ - Show all available commands
- \make build\ - Build Docker image
- \make run\ - Run container
- \make test\ - Test API endpoints
- \make security\ - Run security scan
- \make clean\ - Clean up containers

## 📊 Testing Checklist

- [ ] API starts without errors
- [ ] Health endpoint responds (http://localhost:8000/health)
- [ ] OpenAPI docs accessible (http://localhost:8000/docs)
- [ ] Authentication works
- [ ] Protected endpoints require valid tokens
- [ ] Security scan passes

## 🔒 Security Features Included

- ✅ Secure XML parsing (defusedxml)
- ✅ Environment-based configuration
- ✅ Production-ready settings
- ✅ Security headers middleware
- ✅ Input validation
- ✅ No hardcoded secrets

## 📝 Next Steps

1. Start the application using Docker or locally
2. Test all endpoints
3. Review security scan results
4. Deploy to production when ready

Happy coding! 🎉
