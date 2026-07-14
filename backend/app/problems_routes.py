from datetime import date

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db
from .models import CodingProblem


problems_bp = Blueprint(
    "problems",
    __name__,
    url_prefix="/api/problems",
)


ALLOWED_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard",
}

ALLOWED_STATUSES = {
    "Unsolved",
    "Solved",
    "Revision Needed",
}

ALLOWED_REVISION_STATUSES = {
    "Not Started",
    "First Revision",
    "Second Revision",
    "Mastered",
}


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


def error_response(message, errors=None, status_code=400):
    """Return a consistent error JSON response."""

    return (
        jsonify(
            {
                "success": False,
                "message": message,
                "errors": errors if errors is not None else {},
            }
        ),
        status_code,
    )


def get_json_body():
    """Return a JSON dictionary or None for an invalid request body."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data


def is_non_negative_integer(value):
    """Return whether a value is an integer greater than or equal to zero."""

    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def parse_solved_date(value):
    """
    Convert a YYYY-MM-DD string into a date object.

    Returns:
        tuple: (parsed_date, error_message)
    """

    if value is None or value == "":
        return None, None

    if not isinstance(value, str):
        return None, "Solved date must use the YYYY-MM-DD format."

    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, "Solved date must use the YYYY-MM-DD format."


def validate_problem_data(data, existing_problem=None):
    """
    Validate coding-problem input.

    For updates, unspecified values are taken from the existing problem.
    """

    errors = {}

    title = data.get(
        "title",
        existing_problem.title if existing_problem else None,
    )

    platform = data.get(
        "platform",
        existing_problem.platform if existing_problem else "Other",
    )

    platform_link = data.get(
        "platform_link",
        existing_problem.platform_link if existing_problem else None,
    )

    topic = data.get(
        "topic",
        existing_problem.topic if existing_problem else None,
    )

    difficulty = data.get(
        "difficulty",
        existing_problem.difficulty if existing_problem else "Easy",
    )

    status = data.get(
        "status",
        existing_problem.status if existing_problem else "Unsolved",
    )

    attempts = data.get(
        "attempts",
        existing_problem.attempts if existing_problem else 0,
    )

    time_spent_minutes = data.get(
        "time_spent_minutes",
        (
            existing_problem.time_spent_minutes
            if existing_problem
            else 0
        ),
    )

    revision_status = data.get(
        "revision_status",
        (
            existing_problem.revision_status
            if existing_problem
            else "Not Started"
        ),
    )

    notes = data.get(
        "notes",
        existing_problem.notes if existing_problem else None,
    )

    solved_date_value = data.get(
        "solved_date",
        (
            existing_problem.solved_date.isoformat()
            if existing_problem and existing_problem.solved_date
            else None
        ),
    )

    if not isinstance(title, str) or not title.strip():
        errors["title"] = ["Title is required."]
    else:
        title = title.strip()

    if not isinstance(topic, str) or not topic.strip():
        errors["topic"] = ["Topic is required."]
    else:
        topic = topic.strip()

    if not isinstance(platform, str):
        errors["platform"] = ["Platform must be a string."]
    else:
        platform = platform.strip() or "Other"

    if platform_link is not None:
        if not isinstance(platform_link, str):
            errors["platform_link"] = [
                "Platform link must be a string."
            ]
        else:
            platform_link = platform_link.strip() or None

    if difficulty not in ALLOWED_DIFFICULTIES:
        errors["difficulty"] = [
            "Difficulty must be Easy, Medium, or Hard."
        ]

    if status not in ALLOWED_STATUSES:
        errors["status"] = [
            (
                "Status must be Unsolved, Solved, "
                "or Revision Needed."
            )
        ]

    if not is_non_negative_integer(attempts):
        errors["attempts"] = [
            "Attempts must be a non-negative integer."
        ]

    if not is_non_negative_integer(time_spent_minutes):
        errors["time_spent_minutes"] = [
            "Time spent must be a non-negative integer."
        ]

    if revision_status not in ALLOWED_REVISION_STATUSES:
        errors["revision_status"] = [
            (
                "Revision status must be Not Started, "
                "First Revision, Second Revision, or Mastered."
            )
        ]

    if notes is not None and not isinstance(notes, str):
        errors["notes"] = ["Notes must be a string."]
    elif isinstance(notes, str):
        notes = notes.strip() or None

    solved_date, solved_date_error = parse_solved_date(
        solved_date_value
    )

    if solved_date_error:
        errors["solved_date"] = [solved_date_error]

    if status == "Solved" and solved_date is None:
        errors["solved_date"] = [
            "Solved date is required when status is Solved."
        ]

    # A non-solved problem should not retain a solved date.
    if status != "Solved":
        solved_date = None

    cleaned_data = {
        "title": title,
        "platform": platform,
        "platform_link": platform_link,
        "topic": topic,
        "difficulty": difficulty,
        "status": status,
        "attempts": attempts,
        "time_spent_minutes": time_spent_minutes,
        "revision_status": revision_status,
        "notes": notes,
        "solved_date": solved_date,
    }

    return cleaned_data, errors


def get_owned_problem(problem_id):
    """Return a problem belonging to the authenticated user."""

    return CodingProblem.query.filter_by(
        id=problem_id,
        user_id=current_user.id,
    ).first()


@problems_bp.get("")
@auth_required("token")
def list_problems():
    """
    Return coding problems belonging to the authenticated user.

    Supported filters:
    - topic
    - difficulty
    - status
    - revision_status
    - platform
    """

    query = CodingProblem.query.filter_by(
        user_id=current_user.id
    )

    topic = request.args.get("topic", type=str)
    difficulty = request.args.get("difficulty", type=str)
    status = request.args.get("status", type=str)
    revision_status = request.args.get(
        "revision_status",
        type=str,
    )
    platform = request.args.get("platform", type=str)

    filter_errors = {}

    if difficulty and difficulty not in ALLOWED_DIFFICULTIES:
        filter_errors["difficulty"] = [
            "Difficulty must be Easy, Medium, or Hard."
        ]

    if status and status not in ALLOWED_STATUSES:
        filter_errors["status"] = [
            (
                "Status must be Unsolved, Solved, "
                "or Revision Needed."
            )
        ]

    if (
        revision_status
        and revision_status not in ALLOWED_REVISION_STATUSES
    ):
        filter_errors["revision_status"] = [
            (
                "Revision status must be Not Started, "
                "First Revision, Second Revision, or Mastered."
            )
        ]

    if filter_errors:
        return error_response(
            message="Invalid filter values.",
            errors=filter_errors,
            status_code=400,
        )

    if topic:
        query = query.filter(
            CodingProblem.topic == topic.strip()
        )

    if difficulty:
        query = query.filter(
            CodingProblem.difficulty == difficulty
        )

    if status:
        query = query.filter(
            CodingProblem.status == status
        )

    if revision_status:
        query = query.filter(
            CodingProblem.revision_status == revision_status
        )

    if platform:
        query = query.filter(
            CodingProblem.platform == platform.strip()
        )

    problems = query.order_by(
        CodingProblem.created_at.desc(),
        CodingProblem.id.desc(),
    ).all()

    return success_response(
        message="Coding problems retrieved successfully.",
        data={
            "problems": [
                problem.to_dict()
                for problem in problems
            ],
            "count": len(problems),
            "filters": {
                "topic": topic,
                "difficulty": difficulty,
                "status": status,
                "revision_status": revision_status,
                "platform": platform,
            },
        },
    )


@problems_bp.post("")
@auth_required("token")
def create_problem():
    """Create a coding problem for the authenticated user."""

    data = get_json_body()

    if data is None:
        return error_response(
            message="Request body must contain valid JSON.",
            errors={
                "body": ["A valid JSON object is required."],
            },
            status_code=400,
        )

    cleaned_data, errors = validate_problem_data(data)

    if errors:
        return error_response(
            message="Validation failed.",
            errors=errors,
            status_code=400,
        )

    problem = CodingProblem(
        user_id=current_user.id,
        **cleaned_data,
    )

    try:
        db.session.add(problem)
        db.session.commit()

        return success_response(
            message="Coding problem created successfully.",
            data={
                "problem": problem.to_dict(),
            },
            status_code=201,
        )

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Coding problem could not be created.",
            errors={
                "database": [
                    "A database error occurred while creating the problem."
                ],
            },
            status_code=500,
        )


@problems_bp.get("/<int:problem_id>")
@auth_required("token")
def get_problem(problem_id):
    """Return one coding problem owned by the authenticated user."""

    problem = get_owned_problem(problem_id)

    if problem is None:
        return error_response(
            message="Coding problem not found.",
            errors={
                "problem": [
                    (
                        "The problem does not exist or does not "
                        "belong to the authenticated user."
                    )
                ],
            },
            status_code=404,
        )

    return success_response(
        message="Coding problem retrieved successfully.",
        data={
            "problem": problem.to_dict(),
        },
    )


@problems_bp.put("/<int:problem_id>")
@auth_required("token")
def update_problem(problem_id):
    """Update one coding problem owned by the authenticated user."""

    problem = get_owned_problem(problem_id)

    if problem is None:
        return error_response(
            message="Coding problem not found.",
            errors={
                "problem": [
                    (
                        "The problem does not exist or does not "
                        "belong to the authenticated user."
                    )
                ],
            },
            status_code=404,
        )

    data = get_json_body()

    if data is None:
        return error_response(
            message="Request body must contain valid JSON.",
            errors={
                "body": ["A valid JSON object is required."],
            },
            status_code=400,
        )

    cleaned_data, errors = validate_problem_data(
        data,
        existing_problem=problem,
    )

    if errors:
        return error_response(
            message="Validation failed.",
            errors=errors,
            status_code=400,
        )

    for field, value in cleaned_data.items():
        setattr(problem, field, value)

    try:
        db.session.commit()

        return success_response(
            message="Coding problem updated successfully.",
            data={
                "problem": problem.to_dict(),
            },
        )

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Coding problem could not be updated.",
            errors={
                "database": [
                    "A database error occurred while updating the problem."
                ],
            },
            status_code=500,
        )


@problems_bp.delete("/<int:problem_id>")
@auth_required("token")
def delete_problem(problem_id):
    """Delete one coding problem owned by the authenticated user."""

    problem = get_owned_problem(problem_id)

    if problem is None:
        return error_response(
            message="Coding problem not found.",
            errors={
                "problem": [
                    (
                        "The problem does not exist or does not "
                        "belong to the authenticated user."
                    )
                ],
            },
            status_code=404,
        )

    problem_data = problem.to_dict()

    try:
        db.session.delete(problem)
        db.session.commit()

        return success_response(
            message="Coding problem deleted successfully.",
            data={
                "problem": problem_data,
            },
        )

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Coding problem could not be deleted.",
            errors={
                "database": [
                    "A database error occurred while deleting the problem."
                ],
            },
            status_code=500,
        )