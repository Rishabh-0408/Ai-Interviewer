"""Top-level API router — /api/v1."""

from fastapi import APIRouter

from app.api.auth.routes import router as auth_router
from app.api.candidates.routes import router as candidates_router
from app.api.resumes.routes import router as resumes_router
from app.api.jobs.routes import router as jobs_router
from app.api.interviews.routes import router as interviews_router
from app.api.reports.routes import router as reports_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(candidates_router, prefix="/profile", tags=["Candidate Profile"])
api_router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Job Descriptions"])
api_router.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
