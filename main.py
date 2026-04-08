"""
DebugTraceEnv - FastAPI application entry point
This module maintains backward compatibility with existing server setup.
For OpenEnv multi-mode deployment, use: python -m server.app
"""

from server.app import app
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7860)
