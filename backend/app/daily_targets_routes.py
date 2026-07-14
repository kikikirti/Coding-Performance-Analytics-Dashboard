from datetime import date

from flask import Blueprint, jsonify, request
from flask_security import auth_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .extensions import db
from .models import CodingProblem, DailyTarget


daily_targets_bp = Blueprint(
    "daily_targets",
    __name__,
    url_prefix="/api/daily-targets",
)


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
    """Return the JSON request body as a dictionary."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data


def is_positive_integer(value):
    """Return whether a value is an integer greater than zero."""

    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value > 0
    )


def parse_target_date(value):
    """
    Parse a target date in YYYY-MM-DD format.

    Returns:
        tuple: parsed date and validation error.
    """

    if value is None or value == "":
        return None, "Target date is required."

    if not isinstance(value, str):
        return None, "Target date must use the YYYY-MM-DD format."

    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, "Target date must use the YYYY-MM-DD format."


def count_solved_problems(user_id, target_date):
    """Count solved problems belonging to a user on a specific date."""

    solved_count = (
        db.session.query(func.count(CodingProblem.id))
        .filter(
            CodingProblem.user_id == user_id,
            CodingProblem.status == "Solved",
            CodingProblem.solved_date == target_date,
        )
        .scalar()
    )

    return int(solved_count or 0)


def refresh_solved_count(target):
    """
    Synchronize a daily target's solved count with CodingProblem records.

    Returns True when the stored count was changed.
    """

    calculated_count = count_solved_problems(
        user_id=target.user_id,
        target_date=target.target_date,
    )

    if target.solved_count != calculated_count:
        target.solved_count = calculated_count
        return True

    return False


def get_owned_target(target_id):
    """Return a daily target belonging to the current user."""

    return DailyTarget.query.filter_by(
        id=target_id,
        user_id=current_user.id,
    ).first()


def validate_target_data(data, existing_target=None):
    """Validate daily-target creation or update data."""

    errors = {}

    if existing_target is None:
        target_date_value = data.get("target_date")
        target_count = data.get("target_count")
    else:
        target_date_value = data.get(
            "target_date",
            existing_target.target_date.isoformat(),
        )

        target_count = data.get(
            "target_count",
            existing_target.target_count,
        )

    target_date, target_date_error = parse_target_date(
        target_date_value
    )

    if target_date_error:
        errors["target_date"] = [target_date_error]

    if not is_positive_integer(target_count):
        errors["target_count"] = [
            "Target count must be an integer greater than 0."
        ]

    cleaned_data = {
        "target_date": target_date,
        "target_count": target_count,
    }

    return cleaned_data, errors


@daily_targets_bp.get("")
@auth_required("token")
def list_daily_targets():
    """Return all daily targets belonging to the current user."""

    targets = (
        DailyTarget.query
        .filter_by(user_id=current_user.id)
        .order_by(
            DailyTarget.target_date.desc(),
            DailyTarget.id.desc(),
        )
        .all()
    )

    counts_changed = False

    for target in targets:
        if refresh_solved_count(target):
            counts_changed = True

    if counts_changed:
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

            return error_response(
                message="Daily targets could not be synchronized.",
                errors={
                    "database": [
                        "A database error occurred while calculating solved counts."
                    ],
                },
                status_code=500,
            )

    return success_response(
        message="Daily targets retrieved successfully.",
        data={
            "daily_targets": [
                target.to_dict()
                for target in targets
            ],
            "count": len(targets),
        },
    )


@daily_targets_bp.post("")
@auth_required("token")
def create_daily_target():
    """Create one daily target for the authenticated user."""

    data = get_json_body()

    if data is None:
        return error_response(
            message="Request body must contain valid JSON.",
            errors={
                "body": [
                    "A valid JSON object is required."
                ],
            },
            status_code=400,
        )

    cleaned_data, errors = validate_target_data(data)

    if errors:
        return error_response(
            message="Validation failed.",
            errors=errors,
            status_code=400,
        )

    existing_target = DailyTarget.query.filter_by(
        user_id=current_user.id,
        target_date=cleaned_data["target_date"],
    ).first()

    if existing_target is not None:
        return error_response(
            message="A daily target already exists for this date.",
            errors={
                "target_date": [
                    "Each user can create only one target per date."
                ],
            },
            status_code=409,
        )

    calculated_solved_count = count_solved_problems(
        user_id=current_user.id,
        target_date=cleaned_data["target_date"],
    )

    target = DailyTarget(
        user_id=current_user.id,
        target_date=cleaned_data["target_date"],
        target_count=cleaned_data["target_count"],
        solved_count=calculated_solved_count,
    )

    try:
        db.session.add(target)
        db.session.commit()

        return success_response(
            message="Daily target created successfully.",
            data={
                "daily_target": target.to_dict(),
            },
            status_code=201,
        )

    except IntegrityError:
        db.session.rollback()

        return error_response(
            message="A daily target already exists for this date.",
            errors={
                "target_date": [
                    "Each user can create only one target per date."
                ],
            },
            status_code=409,
        )

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Daily target could not be created.",
            errors={
                "database": [
                    "A database error occurred while creating the target."
                ],
            },
            status_code=500,
        )


@daily_targets_bp.get("/today")
@auth_required("token")
def get_today_target():
    """Return today's target and its calculated completion."""

    today = date.today()

    target = DailyTarget.query.filter_by(
        user_id=current_user.id,
        target_date=today,
    ).first()

    if target is None:
        return error_response(
            message="No daily target exists for today.",
            errors={
                "daily_target": [
                    "Create a target for today before requesting it."
                ],
            },
            status_code=404,
        )

    try:
        if refresh_solved_count(target):
            db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Today's target could not be synchronized.",
            errors={
                "database": [
                    "A database error occurred while calculating solved count."
                ],
            },
            status_code=500,
        )

    return success_response(
        message="Today's daily target retrieved successfully.",
        data={
            "daily_target": target.to_dict(),
        },
    )


@daily_targets_bp.put("/<int:target_id>")
@auth_required("token")
def update_daily_target(target_id):
    """Update a daily target belonging to the current user."""

    target = get_owned_target(target_id)

    if target is None:
        return error_response(
            message="Daily target not found.",
            errors={
                "daily_target": [
                    (
                        "The target does not exist or does not "
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
                "body": [
                    "A valid JSON object is required."
                ],
            },
            status_code=400,
        )

    cleaned_data, errors = validate_target_data(
        data,
        existing_target=target,
    )

    if errors:
        return error_response(
            message="Validation failed.",
            errors=errors,
            status_code=400,
        )

    duplicate_target = (
        DailyTarget.query
        .filter(
            DailyTarget.user_id == current_user.id,
            DailyTarget.target_date == cleaned_data["target_date"],
            DailyTarget.id != target.id,
        )
        .first()
    )

    if duplicate_target is not None:
        return error_response(
            message="A daily target already exists for this date.",
            errors={
                "target_date": [
                    "Each user can create only one target per date."
                ],
            },
            status_code=409,
        )

    target.target_date = cleaned_data["target_date"]
    target.target_count = cleaned_data["target_count"]

    # solved_count is always recalculated from solved problems.
    target.solved_count = count_solved_problems(
        user_id=current_user.id,
        target_date=target.target_date,
    )

    try:
        db.session.commit()

        return success_response(
            message="Daily target updated successfully.",
            data={
                "daily_target": target.to_dict(),
            },
        )

    except IntegrityError:
        db.session.rollback()

        return error_response(
            message="A daily target already exists for this date.",
            errors={
                "target_date": [
                    "Each user can create only one target per date."
                ],
            },
            status_code=409,
        )

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Daily target could not be updated.",
            errors={
                "database": [
                    "A database error occurred while updating the target."
                ],
            },
            status_code=500,
        )


@daily_targets_bp.delete("/<int:target_id>")
@auth_required("token")
def delete_daily_target(target_id):
    """Delete a daily target belonging to the current user."""

    target = get_owned_target(target_id)

    if target is None:
        return error_response(
            message="Daily target not found.",
            errors={
                "daily_target": [
                    (
                        "The target does not exist or does not "
                        "belong to the authenticated user."
                    )
                ],
            },
            status_code=404,
        )

    target_data = target.to_dict()

    try:
        db.session.delete(target)
        db.session.commit()

        return success_response(
            message="Daily target deleted successfully.",
            data={
                "daily_target": target_data,
            },
        )

    except SQLAlchemyError:
        db.session.rollback()

        return error_response(
            message="Daily target could not be deleted.",
            errors={
                "database": [
                    "A database error occurred while deleting the target."
                ],
            },
            status_code=500,
        )