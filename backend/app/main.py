import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware
from backend.app.db.session import init_db
from backend.app.api.auth import router as auth_router
from backend.app.api.events import router as events_router
from backend.app.api.registrations import router as registrations_router
from backend.app.api.admin import router as admin_router
from backend.app.api.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    logger.info("Initializing database schema...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Secure Software Engineering Laboratory Project - Online Event Registration System",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # Secure docs exposure
    redoc_url=None
)

# 1. Custom Security Headers & Request Logging Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# 2. CORS configuration with explicit credentials and allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# 3. Secure Exception Handlers (Preventing internal implementation leaks)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        errors.append(f"{loc}: {err.get('msg')}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Input validation error: " + "; ".join(errors),
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def global_generic_exception_handler(request: Request, exc: Exception):
    # Log internal error without exposing sensitive details to caller
    logger.error(f"Unhandled server error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Please contact system administrator.",
            "status_code": 500
        }
    )


# 4. Include Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(events_router, prefix=settings.API_PREFIX)
app.include_router(registrations_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(health_router)


@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "documentation": "/docs" if settings.DEBUG else "Protected in production mode"
    }
