from uuid import uuid4

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from flask_security import (
    auth_required,
    current_user,
    hash_password,
    verify_and_update_password,
)
from sqlalchemy.exc import IntegrityError

from .extensions import db, security


auth_bp = Blueprint("auth", __name__)


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


def get_json_data():
    """Read the request body without raising an HTML error."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data


def normalize_email(email):
    """Validate and normalize an email address."""

    validated_email = validate_email(
        email,
        check_deliverability=False,
    )

    return validated_email.normalized.lower()


@auth_bp.post("/register")
def register():
    """
    Register a new student account.

    Expected JSON:
    {
        "email": "student@example.com",
        "password": "Password123"
    }
    """

    data = get_json_data()

    if data is None:
        return error_response(
            message="Request body must contain valid JSON.",
            errors={
                "body": ["A valid JSON object is required."],
            },
            status_code=400,
        )

    raw_email = data.get("email")
    password = data.get("password")

    errors = {}

    if not isinstance(raw_email, str) or not raw_email.strip():
        errors["email"] = ["Email is required."]

    if not isinstance(password, str) or not password:
        errors["password"] = ["Password is required."]
    elif len(password) < 8:
        errors["password"] = [
            "Password must contain at least 8 characters."
        ]

    if errors:
        return error_response(
            message="Validation failed.",
            errors=errors,
            status_code=400,
        )

    try:
        email = normalize_email(raw_email.strip())
    except EmailNotValidError as exc:
        return error_response(
            message="Validation failed.",
            errors={
                "email": [str(exc)],
            },
            status_code=400,
        )

    existing_user = security.datastore.find_user(
        email=email,
    )

    if existing_user is not None:
        return error_response(
            message="A user with this email already exists.",
            errors={
                "email": ["This email is already registered."],
            },
            status_code=409,
        )

    try:
        student_role = security.datastore.find_or_create_role(
            name="student",
            description=(
                "Student account for tracking coding performance."
            ),
        )

        user = security.datastore.create_user(
            email=email,
            password=hash_password(password),
            active=True,
            fs_uniquifier=uuid4().hex,
            roles=[student_role],
        )

        db.session.commit()

        return success_response(
            message="Registration successful.",
            data={
                "user": user.to_dict(),
            },
            status_code=201,
        )

    except IntegrityError:
        db.session.rollback()

        return error_response(
            message="A user with this email already exists.",
            errors={
                "email": ["This email is already registered."],
            },
            status_code=409,
        )

    except Exception:
        db.session.rollback()

        return error_response(
            message="Registration could not be completed.",
            errors={
                "server": ["An unexpected server error occurred."],
            },
            status_code=500,
        )


@auth_bp.post("/login")
def login():
    """
    Authenticate a user and return an authentication token.

    Expected JSON:
    {
        "email": "student@example.com",
        "password": "Password123"
    }
    """

    data = get_json_data()

    if data is None:
        return error_response(
            message="Request body must contain valid JSON.",
            errors={
                "body": ["A valid JSON object is required."],
            },
            status_code=400,
        )

    raw_email = data.get("email")
    password = data.get("password")

    errors = {}

    if not isinstance(raw_email, str) or not raw_email.strip():
        errors["email"] = ["Email is required."]

    if not isinstance(password, str) or not password:
        errors["password"] = ["Password is required."]

    if errors:
        return error_response(
            message="Validation failed.",
            errors=errors,
            status_code=400,
        )

    try:
        email = normalize_email(raw_email.strip())
    except EmailNotValidError:
        return error_response(
            message="Invalid email or password.",
            errors={
                "credentials": [
                    "The supplied email or password is incorrect."
                ],
            },
            status_code=401,
        )

    user = security.datastore.find_user(
        email=email,
    )

    if user is None:
        return error_response(
            message="Invalid email or password.",
            errors={
                "credentials": [
                    "The supplied email or password is incorrect."
                ],
            },
            status_code=401,
        )

    if not user.active:
        return error_response(
            message="This user account is inactive.",
            errors={
                "account": ["The account has been deactivated."],
            },
            status_code=403,
        )

    if not verify_and_update_password(password, user):
        return error_response(
            message="Invalid email or password.",
            errors={
                "credentials": [
                    "The supplied email or password is incorrect."
                ],
            },
            status_code=401,
        )

    # Required because verify_and_update_password() can update an old hash.
    db.session.commit()

    authentication_token = user.get_auth_token()

    return success_response(
        message="Login successful.",
        data={
            "authentication_token": authentication_token,
            "token_header": "Authentication-Token",
            "user": user.to_dict(),
        },
        status_code=200,
    )


@auth_bp.get("/profile")
@auth_required("token")
def profile():
    """Return the currently authenticated user's profile."""

    return success_response(
        message="Profile retrieved successfully.",
        data={
            "user": current_user.to_dict(),
        },
        status_code=200,
    )