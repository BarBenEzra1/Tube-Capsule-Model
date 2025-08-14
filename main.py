from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.simulation_router import router as simulation_router
from app.routers.system_router import router as system_router
from app.routers.tube_router import router as tube_router
from app.routers.coil_router import router as coil_router
from app.routers.capsule_router import router as capsule_router

app = FastAPI(
    title="Tube Capsule Model API",
    description="API for simulating tube capsule system",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tube_router)
app.include_router(coil_router)
app.include_router(capsule_router)
app.include_router(system_router)
app.include_router(simulation_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 