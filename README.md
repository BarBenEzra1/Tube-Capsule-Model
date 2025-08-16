# Tube Capsule Model API

A physics simulation API for modeling capsule movement through tube systems with electromagnetic coils. 
This project provides a FastAPI-based REST API for creating, managing, and simulating the system.

## 🚀 Features

- **Physics-based Simulation**: Accurate modeling of capsule acceleration and constant velocity segments
- **RESTful API**: Complete CRUD operations for all system components
- **Real-time Simulation**: Generate detailed trajectory data including position, velocity, and acceleration over time
- **Energy Consumption Tracking**: Monitor energy usage by electromagnetic coils during acceleration phases
- **Compressed Results**: Automatic compression of simulation results for efficient data transfer
- **Interactive Documentation**: Built-in Swagger UI and ReDoc documentation

## 🏗️ System Components

### Core Entities

- **Tube**: The transport tunnel with a defined length
- **Capsule**: The transport vehicle with mass and initial velocity properties
- **Coil**: Electromagnetic acceleration coils with configurable force applied on capsule within a defined length
- **System**: Combines a tube, capsule, and positioned coils into a complete transport system
- **Segments**: Individual simulation segments representing different phases of capsule movement

![Diagram](docs/system_components_diagram.png)

### Model Behavior

1. The simulation is 1D
2. Acceleration starts at the midpoint of a coil and continues until its end
3. Capsule moves at constant velocity outside coils
4. Coils apply constant force
5. One capsule per simulation run
6. Ignoring friction (coil force is the only force applied)
7. Assuming a single user issues only one API request at a time.

### Simulation Flow

Capsule starts at the tube entrance at t0 = 0 and moves left to right at its initial constant velocity.
Capsule passes through coils in order of their positions.
Upon reaching a coil’s center, the coil’s configured force is applied on the capsule, causing acceleration.
Acceleration continues until the capsule exits the coil.
After exiting, it maintains the velocity reached at that moment until the next coil or the end of the tube.

The simulation divides capsule movement into discrete segments.
If the tube contains no coils, it is treated as a single constant velocity segment from start to end.
For tubes with coils, the segmentation follows this pattern:
1.	First segment (constant velocity): From the tube's beginning (position 0) to the midpoint of the first coil.
2.	For each coil, two segments are created:

    •	Acceleration segment: From the coil's midpoint to the coil's end, where the capsule accelerates due to the coil's force.
    
    •	Constant velocity segment: From the coil’s end to either the midpoint of the next coil (if it exists) or to the tube’s end (for the last coil).

![Diagram](docs/system_segments.png)

## 📋 Prerequisites

You only need to have Docker and Docker Compose installed on your system:

- **Docker Desktop** (includes Docker Compose): [Download here](https://www.docker.com/products/docker-desktop/)
- Or install **Docker** and **Docker Compose** separately on Linux

## 🚀 Quick Start

1. **Clone or download this project** to your local machine

2. **Navigate to the project directory:**
   ```bash
   cd tube-capsule-model
   ```

3. **Start the application:**
   ```bash
   docker compose up --build
   ```

4. **Wait for the services to start** (first time may take a few minutes to download images and build)

5. **Access the Swagger UI** in your browser:
   ```
   http://localhost:8000/docs
   ```

That's it! 🎉

Once running, you can access:

- **Swagger UI (Interactive API docs)**: http://localhost:8000/docs
- **ReDoc (Alternative docs)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## 🗄️ Database Access

The PostgreSQL database runs in a Docker container and is accessible at:
- **Host**: localhost
- **Port**: 5432
- **Database**: tube_capsule_db
- **Username**: postgres
- **Password**: password

You can connect using any PostgreSQL client (pgAdmin, DBeaver, etc.) or command line:
```bash
docker exec -it tube-capsule-postgres psql -U postgres -d tube_capsule_db
```

## 📚 API Endpoints

### Tubes
- `POST /tubes/` - Create a new tube
- `GET /tubes/{tube_id}` - Get tube by ID
- `PUT /tubes/{tube_id}` - Update tube
- `DELETE /tubes/{tube_id}` - Delete tube
- `GET /tubes/` - List all tubes

### Capsules
- `POST /capsules/` - Create a new capsule
- `GET /capsules/{capsule_id}` - Get capsule by ID
- `PUT /capsules/{capsule_id}` - Update capsule
- `DELETE /capsules/{capsule_id}` - Delete capsule
- `GET /capsules/` - List all capsules

### Coils
- `POST /coils/` - Create a new electromagnetic coil
- `GET /coils/{coil_id}` - Get coil by ID
- `PUT /coils/{coil_id}` - Update coil
- `DELETE /coils/{coil_id}` - Delete coil
- `GET /coils/` - List all coils

### Systems
- `POST /systems/` - Create a new system
- `GET /systems/{system_id}` - Get system by ID
- `PUT /systems/{system_id}` - Update system
- `DELETE /systems/{system_id}` - Delete system
- `GET /systems/` - List all systems

### Simulation
- `POST /simulation/` - Run physics simulation and download results

## 🔬 Usage Example

### 1. Create System Components

**Create a Tube**:
```bash
curl -X POST "http://localhost:8000/tubes/" \
  -H "Content-Type: application/json" \
  -d '{"length": 5.0}'
```

**Create a Capsule**:
```bash
curl -X POST "http://localhost:8000/capsules/" \
  -H "Content-Type: application/json" \
  -d '{"mass": 1.0, "initial_velocity": 0.5}'
```

**Create Coils**:
```bash
curl -X POST "http://localhost:8000/coils/" \
  -H "Content-Type: application/json" \
  -d '{"length": 0.3, "force_applied": 10}'
```

### 2. Create a System

```bash
curl -X POST "http://localhost:8000/systems/" \
  -H "Content-Type: application/json" \
  -d '{
    "tube_id": 1,
    "capsule_id": 1,
    "coil_ids_to_positions": [
      {"coilId": 1, "position": 0.5},
    ]
  }'
```

### 3. Run Simulation

```bash
curl -X POST "http://localhost:8000/simulation/" \
  -H "Content-Type: application/json" \
  -d '{"system_id": 1}' \
  --output simulation_result.json.gz
```

### 4. Complete Flow Simulation (All-in-One)

For convenience, you can create all entities and run the simulation in a single request:

```bash
curl -X POST "http://localhost:8000/simulation/complete-flow" \
  -H "Content-Type: application/json" \
  -d '{
    "tube": {
      "length": 1000.0
    },
    "capsule": {
      "mass": 100.0,
      "initial_velocity": 10.0
    },
    "coils": [
      {
        "length": 50.0,
        "force_applied": 1000.0,
        "position": 200.0
      },
      {
        "length": 60.0,
        "force_applied": 1200.0,
        "position": 500.0
      },
      {
        "length": 40.0,
        "force_applied": 800.0,
        "position": 800.0
      }
    ]
  }' \
  --output simulation_result.json.gz
```

This endpoint automatically:
- Creates a tube with the specified length
- Creates a capsule with the specified mass and initial velocity
- Creates all coils with their properties and positions
- Assembles them into a system
- Runs the simulation
- Returns the compressed simulation results

The simulation returns a compressed JSON file containing:
- Complete position vs. time trajectory points
- Velocity vs. time trajectory points
- Acceleration vs. time trajectory points
- Force applied vs. time trajectory points
- Total energy consumed vs. time trajectory points
- Coil engagement logs
- Summary statistics (total travel time, final velocity)

## 📊 Simulation Output

The simulation generates comprehensive trajectory data:

```json
{
  "success": true,
  "result": {
    "system_id": 2,
    "system_details": [
      {
        "tube": {
          "id": 3,
          "length": 5.0
        },
        "capsule": {
          "id": 3,
          "mass": 1.0,
          "initial_velocity": 0.5
        },
        "coils": [
          {"id": 3, "length": 0.3, "force_applied": 10.0, "position": 0.5}
        ]
      }
    ],
    "total_travel_time_s": 3.760018387919162,
    "final_velocity_mps": 1.8027756377319946,
    "total_energy_consumed_j": 1.5,
    "position_vs_time_trajectory": [
      {
        "time": 0.0,
        "position": 0.0
      },
      {
        "time": 1.3,
        "position": 0.65
      },
      {
        "time": 1.4302775637731995,
        "position": 0.8
      },
      {
        "time": 3.760018387919162,
        "position": 5.0
      }
    ],
    "velocity_vs_time_trajectory": [
      {
        "time": 0.0,
        "velocity": 0.5
      },
      {
        "time": 1.3,
        "velocity": 1.8027756377319946
      },
      {
        "time": 1.4302775637731995,
        "velocity": 1.8027756377319946
      },
      {
        "time": 3.760018387919162,
        "velocity": 1.8027756377319946
      }
    ],
    "acceleration_vs_time_trajectory": [
      {
        "time": 0.0,
        "acceleration": 0.0
      },
      {
        "time": 1.3,
        "acceleration": 10.0
      },
      {
        "time": 1.4302775637731995,
        "acceleration": 0.0
      },
      {
        "time": 3.760018387919162,
        "acceleration": 0.0
      }
    ],
    "force_applied_vs_time_trajectory": [
      {
        "time": 0.0,
        "force_applied": 0.0
      },
      {
        "time": 1.3,
        "force_applied": 10.0
      },
      {
        "time": 1.4302775637731995,
        "force_applied": 0.0
      },
      {
        "time": 3.760018387919162,
        "force_applied": 0.0
      }
    ],
    "total_energy_consumed_vs_time_trajectory": [
      {
        "time": 0.0,
        "total_energy_consumed_j": 0.0
      },
      {
        "time": 1.3,
        "total_energy_consumed_j": 1.5
      },
      {
        "time": 1.4302775637731995,
        "total_energy_consumed_j": 1.5
      },
      {
        "time": 3.760018387919162,
        "total_energy_consumed_j": 1.5
      }
    ],
    "coil_engagement_logs": [
        {"t_s": 0.0, "event": "run_start", "position_m": 0.0, "velocity_mps": 0.5, "acceleration_mps2": 0.0, "force_applied_n": 0.0, "energy_consumed_j": 0.0},
        {"t_s": 1.0, "event": "coil_enter", "coil_id": 3, "position_m": 0.5, "velocity_mps": 0.5, "acceleration_mps2": 0.0, "force_applied_n": 0.0, "energy_consumed_j": 0.0},
        {"t_s": 1.3, "event": "coil_midpoint_accel", "coil_id": 3, "position_m": 0.65, "velocity_mps": 0.5, "acceleration_mps2": 10.0, "force_applied_nN": 10.0, "energy_consumed_j": 0.0},
        {"t_s": 1.4303, "event": "coil_exit", "coil_id": 3, "position_m": 0.8, "velocity_mps": 1.8027756377319946, "acceleration_mps2": 0.0, "acceleration_duration_s": 0.13027756377319946, "acceleration_segment_length_m": 0.15, "force_applied_n": 0.0, "energy_consumed_j": 1.5},
        {"t_s": 3.76, "event": "run_end", "position_m": 5.0, "velocity_mps": 1.8027756377319946, "acceleration_mps2": 0.0, "force_applied_n": 0.0, "energy_consumed_j": 0.0}
    ]
  }
}
```

## 🏛️ Architecture

### Project Structure

```
tube-capsule-model/
├── app/
│   ├── data/                   # JSON-based data storage for system entities
│   ├── database/               # Database configuration & models
│   ├── data_access/            # Data access layer
│   ├── domain/
│   │   ├── entities/           # Core business objects
│   │   ├── schemas/            # Pydantic data models
│   │   ├── services/           # Business logic layer
│   │   └── utils/              # Physics calculations & utilities
│   └── routers/                # FastAPI route handlers
├── docs/                       # Diagrams for README
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Multi-service Docker setup
├── docker-init-db.py           # Database initialization for Docker
├── init_db.py                  # Local database initialization
├── main.py                     # FastAPI application setup
├── run_server.py               # Development server launcher
└── requirements.txt            # Project dependencies
```

### Design Patterns

- **Domain-Driven Design**: Clear separation of entities, services, and schemas
- **Repository Pattern**: File-based data persistence using JSONL format
- **Service Layer**: Business logic abstraction from API endpoints
- **Physics Engine**: Modular physics calculations for realistic simulation

## 🔧 Configuration

### Data Storage

The application uses JSONL (JSON Lines) files for data persistence:
- `app/data/tube.jsonl` - Tube definitions
- `app/data/capsule.jsonl` - Capsule specifications  
- `app/data/coil.jsonl` - Electromagnetic coil data
- `app/data/system.jsonl` - Complete system configurations

### Physics Parameters

Key physics calculations include:
- **Acceleration**: F = ma (Force = mass × acceleration)
- **Kinematic equations**: For position, velocity, and time relationships
- **Energy consumption**: Work = Force × Distance for each coil activation