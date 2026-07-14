from datetime import date, datetime, timezone

from flask_security import RoleMixin, UserMixin

from .extensions import db


def utc_now():
    """Return the current UTC datetime."""

    return datetime.now(timezone.utc)


# Association table for the many-to-many relationship between users and roles.
roles_users = db.Table(
    "roles_users",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(db.Model, RoleMixin):
    """Role assigned to an application user."""

    __tablename__ = "roles"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    def to_dict(self):
        """Return role data in JSON-serializable format."""

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model, UserMixin):
    """Application user who tracks coding preparation progress."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password = db.Column(
        db.String(255),
        nullable=False,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    # Required by Flask-Security-Too.
    fs_uniquifier = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
    )

    roles = db.relationship(
        "Role",
        secondary=roles_users,
        lazy="select",
        backref=db.backref(
            "users",
            lazy="dynamic",
        ),
    )

    coding_problems = db.relationship(
        "CodingProblem",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="select",
    )

    daily_targets = db.relationship(
        "DailyTarget",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="select",
    )

    def to_dict(self):
        """
        Return safe user data.

        The password hash is intentionally excluded.
        """

        return {
            "id": self.id,
            "email": self.email,
            "active": self.active,
            "roles": [role.to_dict() for role in self.roles],
        }

    def __repr__(self):
        return f"<User {self.email}>"


class CodingProblem(db.Model):
    """Coding problem tracked by a user."""

    __tablename__ = "coding_problems"

    DIFFICULTY_VALUES = (
        "Easy",
        "Medium",
        "Hard",
    )

    STATUS_VALUES = (
        "Unsolved",
        "Solved",
        "Revision Needed",
    )

    REVISION_STATUS_VALUES = (
        "Not Started",
        "First Revision",
        "Second Revision",
        "Mastered",
    )

    __table_args__ = (
        db.CheckConstraint(
            "difficulty IN ('Easy', 'Medium', 'Hard')",
            name="ck_coding_problem_difficulty",
        ),
        db.CheckConstraint(
            """
            status IN (
                'Unsolved',
                'Solved',
                'Revision Needed'
            )
            """,
            name="ck_coding_problem_status",
        ),
        db.CheckConstraint(
            """
            revision_status IN (
                'Not Started',
                'First Revision',
                'Second Revision',
                'Mastered'
            )
            """,
            name="ck_coding_problem_revision_status",
        ),
        db.CheckConstraint(
            "attempts >= 0",
            name="ck_coding_problem_attempts_non_negative",
        ),
        db.CheckConstraint(
            "time_spent_minutes >= 0",
            name="ck_coding_problem_time_non_negative",
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    platform = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    platform_link = db.Column(
        db.String(1000),
        nullable=True,
    )

    topic = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False,
        default="Easy",
        index=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Unsolved",
        index=True,
    )

    attempts = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    time_spent_minutes = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    revision_status = db.Column(
        db.String(30),
        nullable=False,
        default="Not Started",
        index=True,
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    solved_date = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user = db.relationship(
        "User",
        back_populates="coding_problems",
    )

    def to_dict(self):
        """Return coding-problem data in JSON-serializable format."""

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "platform": self.platform,
            "platform_link": self.platform_link,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "status": self.status,
            "attempts": self.attempts,
            "time_spent_minutes": self.time_spent_minutes,
            "revision_status": self.revision_status,
            "notes": self.notes,
            "solved_date": (
                self.solved_date.isoformat()
                if self.solved_date
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<CodingProblem id={self.id} "
            f"title={self.title!r} "
            f"status={self.status!r}>"
        )


class DailyTarget(db.Model):
    """Daily coding target created by a user."""

    __tablename__ = "daily_targets"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "target_date",
            name="uq_daily_target_user_date",
        ),
        db.CheckConstraint(
            "target_count > 0",
            name="ck_daily_target_count_positive",
        ),
        db.CheckConstraint(
            "solved_count >= 0",
            name="ck_daily_target_solved_non_negative",
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    target_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    target_count = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    solved_count = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user = db.relationship(
        "User",
        back_populates="daily_targets",
    )

    @property
    def completion_percentage(self):
        """Calculate daily target completion percentage."""

        if self.target_count <= 0:
            return 0.0

        percentage = (
            self.solved_count / self.target_count
        ) * 100

        return min(round(percentage, 2),100.0)

    @property
    def is_completed(self):
        """Return whether the daily target has been achieved."""

        return self.solved_count >= self.target_count

    def to_dict(self):
        """Return daily-target data in JSON-serializable format."""

        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_date": (
                self.target_date.isoformat()
                if self.target_date
                else None
            ),
            "target_count": self.target_count,
            "solved_count": self.solved_count,
            "completion_percentage": self.completion_percentage,
            "is_completed": self.is_completed,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<DailyTarget id={self.id} "
            f"user_id={self.user_id} "
            f"date={self.target_date}>"
        )