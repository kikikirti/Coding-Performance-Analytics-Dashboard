from collections import defaultdict
from datetime import date, timedelta

from flask import Blueprint, jsonify
from flask_security import auth_required, current_user

from .models import CodingProblem, DailyTarget


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard",
)


DIFFICULTIES = (
    "Easy",
    "Medium",
    "Hard",
)

REVISION_STATUSES = (
    "Not Started",
    "First Revision",
    "Second Revision",
    "Mastered",
)

# A topic is treated as having a high revision-needed count
# when at least two problems require revision.
HIGH_REVISION_NEEDED_COUNT = 2


def success_response(message, data=None, status_code=200):
    """Return a consistent successful JSON response."""

    return (
        jsonify(
            {
                "success": True,
                "message": message,
                "data": data if data is not None else {},
            }
        ),
        status_code,
    )


def calculate_percentage(numerator, denominator):
    """Calculate a percentage safely."""

    if denominator <= 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        2,
    )


def get_current_user_problems():
    """Return all problems belonging to the current user."""

    return CodingProblem.query.filter_by(
        user_id=current_user.id
    ).all()


def build_topic_statistics(problems):
    """Create topic-level statistics from coding problems."""

    topic_data = defaultdict(
        lambda: {
            "total_count": 0,
            "solved_count": 0,
            "unsolved_count": 0,
            "revision_needed_count": 0,
            "total_attempts": 0,
        }
    )

    for problem in problems:
        topic = problem.topic.strip()

        topic_data[topic]["total_count"] += 1
        topic_data[topic]["total_attempts"] += (
            problem.attempts or 0
        )

        if problem.status == "Solved":
            topic_data[topic]["solved_count"] += 1

        elif problem.status == "Unsolved":
            topic_data[topic]["unsolved_count"] += 1

        elif problem.status == "Revision Needed":
            topic_data[topic]["revision_needed_count"] += 1

    statistics = []

    for topic, values in topic_data.items():
        total_count = values["total_count"]

        statistics.append(
            {
                "topic": topic,
                "total_count": total_count,
                "solved_count": values["solved_count"],
                "unsolved_count": values["unsolved_count"],
                "revision_needed_count": (
                    values["revision_needed_count"]
                ),
                "total_attempts": values["total_attempts"],
                "average_attempts": round(
                    values["total_attempts"] / total_count,
                    2,
                )
                if total_count > 0
                else 0.0,
                "solved_percentage": calculate_percentage(
                    values["solved_count"],
                    total_count,
                ),
            }
        )

    return statistics


@dashboard_bp.get("/summary")
@auth_required("token")
def dashboard_summary():
    """Return overall coding-performance statistics."""

    problems = get_current_user_problems()

    total_problems = len(problems)

    solved_problems = sum(
        1
        for problem in problems
        if problem.status == "Solved"
    )

    unsolved_problems = sum(
        1
        for problem in problems
        if problem.status == "Unsolved"
    )

    revision_needed_problems = sum(
        1
        for problem in problems
        if problem.status == "Revision Needed"
    )

    total_attempts = sum(
        problem.attempts or 0
        for problem in problems
    )

    total_time_spent_minutes = sum(
        problem.time_spent_minutes or 0
        for problem in problems
    )

    average_attempts_per_problem = (
        round(total_attempts / total_problems, 2)
        if total_problems > 0
        else 0.0
    )

    solved_percentage = calculate_percentage(
        solved_problems,
        total_problems,
    )

    return success_response(
        message="Dashboard summary retrieved successfully.",
        data={
            "total_problems": total_problems,
            "solved_problems": solved_problems,
            "unsolved_problems": unsolved_problems,
            "revision_needed_problems": (
                revision_needed_problems
            ),
            "total_attempts": total_attempts,
            "total_time_spent_minutes": (
                total_time_spent_minutes
            ),
            "average_attempts_per_problem": (
                average_attempts_per_problem
            ),
            "solved_percentage": solved_percentage,
        },
    )


@dashboard_bp.get("/topic-progress")
@auth_required("token")
def topic_progress():
    """Return topic-wise coding progress."""

    problems = get_current_user_problems()
    topics = build_topic_statistics(problems)

    topics.sort(
        key=lambda item: item["topic"].lower()
    )

    clean_topics = []

    for topic in topics:
        clean_topics.append(
            {
                "topic": topic["topic"],
                "total_count": topic["total_count"],
                "solved_count": topic["solved_count"],
                "unsolved_count": topic["unsolved_count"],
                "revision_needed_count": (
                    topic["revision_needed_count"]
                ),
                "solved_percentage": (
                    topic["solved_percentage"]
                ),
            }
        )

    return success_response(
        message="Topic progress retrieved successfully.",
        data={
            "topics": clean_topics,
            "count": len(clean_topics),
        },
    )


@dashboard_bp.get("/difficulty-progress")
@auth_required("token")
def difficulty_progress():
    """Return progress for Easy, Medium, and Hard problems."""

    problems = get_current_user_problems()

    difficulty_statistics = []

    for difficulty in DIFFICULTIES:
        difficulty_problems = [
            problem
            for problem in problems
            if problem.difficulty == difficulty
        ]

        total_count = len(difficulty_problems)

        solved_count = sum(
            1
            for problem in difficulty_problems
            if problem.status == "Solved"
        )

        difficulty_statistics.append(
            {
                "difficulty": difficulty,
                "total_count": total_count,
                "solved_count": solved_count,
                "solved_percentage": calculate_percentage(
                    solved_count,
                    total_count,
                ),
            }
        )

    return success_response(
        message="Difficulty progress retrieved successfully.",
        data={
            "difficulties": difficulty_statistics,
        },
    )


@dashboard_bp.get("/weak-topics")
@auth_required("token")
def weak_topics():
    """
    Return topics that meet at least one weakness condition.

    A topic is weak when:
    - solved percentage is below 60%, or
    - at least two problems need revision, or
    - average attempts are greater than two.
    """

    problems = get_current_user_problems()
    topic_statistics = build_topic_statistics(problems)

    weak_topic_results = []

    for topic in topic_statistics:
        weakness_reasons = []

        if topic["solved_percentage"] < 60:
            weakness_reasons.append(
                "Solved percentage is below 60%."
            )

        if (
            topic["revision_needed_count"]
            >= HIGH_REVISION_NEEDED_COUNT
        ):
            weakness_reasons.append(
                "Revision-needed problem count is high."
            )

        if topic["average_attempts"] > 2:
            weakness_reasons.append(
                "Average attempts are greater than 2."
            )

        if weakness_reasons:
            weak_topic_results.append(
                {
                    "topic": topic["topic"],
                    "total_count": topic["total_count"],
                    "solved_count": topic["solved_count"],
                    "unsolved_count": (
                        topic["unsolved_count"]
                    ),
                    "revision_needed_count": (
                        topic["revision_needed_count"]
                    ),
                    "average_attempts": (
                        topic["average_attempts"]
                    ),
                    "solved_percentage": (
                        topic["solved_percentage"]
                    ),
                    "weakness_reasons": weakness_reasons,
                }
            )

    # Weakest topics are shown first:
    # 1. Lowest solved percentage
    # 2. Highest revision-needed count
    # 3. Highest average attempts
    weak_topic_results.sort(
        key=lambda item: (
            item["solved_percentage"],
            -item["revision_needed_count"],
            -item["average_attempts"],
            item["topic"].lower(),
        )
    )

    return success_response(
        message="Weak topics retrieved successfully.",
        data={
            "weak_topics": weak_topic_results,
            "count": len(weak_topic_results),
            "criteria": {
                "maximum_strong_solved_percentage": 60,
                "high_revision_needed_count": (
                    HIGH_REVISION_NEEDED_COUNT
                ),
                "maximum_average_attempts": 2,
            },
        },
    )


@dashboard_bp.get("/revision-summary")
@auth_required("token")
def revision_summary():
    """Return counts for each revision status."""

    problems = get_current_user_problems()

    revision_counts = {
        revision_status: 0
        for revision_status in REVISION_STATUSES
    }

    for problem in problems:
        if problem.revision_status in revision_counts:
            revision_counts[problem.revision_status] += 1

    return success_response(
        message="Revision summary retrieved successfully.",
        data={
            "revision_status_counts": revision_counts,
            "total_problems": len(problems),
        },
    )


@dashboard_bp.get("/daily-target-summary")
@auth_required("token")
def daily_target_summary():
    """Return today's target and recent solving progress."""

    today = date.today()
    seven_day_start = today - timedelta(days=6)

    today_target_record = DailyTarget.query.filter_by(
        user_id=current_user.id,
        target_date=today,
    ).first()

    today_solved = CodingProblem.query.filter_by(
        user_id=current_user.id,
        status="Solved",
        solved_date=today,
    ).count()

    today_target = (
        today_target_record.target_count
        if today_target_record
        else 0
    )

    completion_percentage = calculate_percentage(
        today_solved,
        today_target,
    )

    completion_percentage = min(
        completion_percentage,
        100.0,
    )

    remaining_today = max(
        today_target - today_solved,
        0,
    )

    last_7_days_solved_count = (
        CodingProblem.query
        .filter(
            CodingProblem.user_id == current_user.id,
            CodingProblem.status == "Solved",
            CodingProblem.solved_date >= seven_day_start,
            CodingProblem.solved_date <= today,
        )
        .count()
    )

    return success_response(
        message="Daily target summary retrieved successfully.",
        data={
            "today_target": today_target,
            "today_solved": today_solved,
            "completion_percentage": completion_percentage,
            "remaining_today": remaining_today,
            "last_7_days_solved_count": (
                last_7_days_solved_count
            ),
            "target_exists": today_target_record is not None,
            "target_date": today.isoformat(),
        },
    )