from sqlalchemy import Column, Integer, Float, String, DateTime, Index, JSON
from sqlalchemy.sql import func
from .config import Base


class EngagementEvent(Base):
    """
    Time series table for storing simulation events.
    Each event represents a point in time during a simulation run.
    """
    __tablename__ = "engagement_events"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(50), nullable=False, index=True)
    system_id = Column(Integer, nullable=False, index=True)
    timestamp_s = Column(Float, nullable=False, index=True)
    event = Column(String(50), nullable=False, index=True)
    coil_id = Column(Integer, nullable=True, index=True)
    position_m = Column(Float, nullable=False)
    velocity_mps = Column(Float, nullable=False)
    acceleration_mps2 = Column(Float, nullable=False)
    acceleration_duration_s = Column(Float, nullable=True)
    acceleration_segment_length_m = Column(Float, nullable=True)
    force_applied_n = Column(Float, nullable=False)
    energy_consumed_j = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_simulation_time', 'simulation_id', 'timestamp_s'),
        Index('idx_system_time', 'system_id', 'timestamp_s'),
        Index('idx_event_time', 'event', 'timestamp_s'),
        Index('idx_coil_time', 'coil_id', 'timestamp_s'),
    )


class SimulationRun(Base):
    """
    Table for storing simulation run metadata and summary statistics.
    """
    __tablename__ = "simulation_runs"

    id = Column(String(50), primary_key=True)
    system_id = Column(Integer, nullable=False, index=True)
    system_details = Column(JSON, nullable=False)
    total_travel_time_s = Column(Float, nullable=True)
    final_velocity_mps = Column(Float, nullable=True)
    total_energy_consumed_j = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running")  # running, completed, failed 