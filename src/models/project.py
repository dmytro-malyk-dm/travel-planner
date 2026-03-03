from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class TravelProject(Base):
    __tablename__ = "travel_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    places: Mapped[List["ProjectPlace"]] = relationship(
        "ProjectPlace", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TravelProject(id={self.id}, name={self.name})>"


class ProjectPlace(Base):
    __tablename__ = "project_places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_visited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("travel_projects.id", ondelete="CASCADE"), nullable=False
    )
    project: Mapped["TravelProject"] = relationship(
        "TravelProject", back_populates="places"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_project_place"),
    )

    def __repr__(self):
        return f"<ProjectPlace(id={self.id}, external_id={self.external_id})>"
