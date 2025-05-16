from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.limiter import init_limiter, close_limiter

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "Welcome to Kurobara Manga Manager API"}


@app.on_event("startup")
async def startup():
    # Initialize rate limiter if enabled
    if hasattr(settings, 'RATE_LIMITING_ENABLED') and settings.RATE_LIMITING_ENABLED:
        try:
            await init_limiter()
        except Exception as e:
            print(f"Warning: Rate limiting initialization failed: {e}")
            print("The application will continue without rate limiting")


@app.on_event("shutdown")
async def shutdown():
    # Close rate limiter connection
    if hasattr(settings, 'RATE_LIMITING_ENABLED') and settings.RATE_LIMITING_ENABLED:
        await close_limiter()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
