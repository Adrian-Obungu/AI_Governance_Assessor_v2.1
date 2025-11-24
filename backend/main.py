from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from backend.config import settings
from backend.auth.router import router as auth_router
from backend.assessments.router import router as assessments_router
from backend.audit.logging import logger, log_request, log_error

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="AI Governance Assessor API",
    description="API for AI governance assessments with authentication and reporting",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request
        log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code
        )
        
        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    except Exception as e:
        log_error(e, f"{request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )


# Include routers
app.include_router(auth_router)
app.include_router(assessments_router)


@app.get("/")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": "AI Governance Assessor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.environment == "development"
    )
