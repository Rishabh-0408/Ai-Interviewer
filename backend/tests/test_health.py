"""Health check endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test the /health endpoint returns 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AI Interviewer"


@pytest.mark.asyncio
async def test_api_docs_accessible(client):
    """Test that the Swagger UI docs page is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200
