from collections import Counter
from datetime import date, timedelta
import re
from typing import NamedTuple
from uuid import uuid4

from flask_security import hash_password

from app import create_app
from app.extensions import db
from app.models import CodingProblem, DailyTarget, Role, User


DEMO_EMAIL = "student@example.com"
DEMO_PASSWORD = "student123"


class ProblemSeed(NamedTuple):
    title: str
    platform: str
    topic: str
    difficulty: str
    status: str
    attempts: int
    time_spent_minutes: int
    revision_status: str
    solved_days_ago: int | None
    focus: str


SAMPLE_PROBLEMS = [
    ProblemSeed(
        "Two Sum",
        "LeetCode",
        "Array",
        "Easy",
        "Solved",
        1,
        20,
        "First Revision",
        0,
        "hash-map lookup",
    ),
    ProblemSeed(
        "Best Time to Buy and Sell Stock",
        "HackerRank",
        "Array",
        "Easy",
        "Solved",
        2,
        25,
        "Mastered",
        1,
        "single-pass minimum tracking",
    ),
    ProblemSeed(
        "Contains Duplicate",
        "CodeChef",
        "Array",
        "Easy",
        "Solved",
        1,
        15,
        "Mastered",
        2,
        "set-based duplicate detection",
    ),
    ProblemSeed(
        "Move Zeroes",
        "GeeksforGeeks",
        "Array",
        "Easy",
        "Solved",
        2,
        25,
        "First Revision",
        3,
        "two-pointer in-place movement",
    ),
    ProblemSeed(
        "Maximum Subarray",
        "LeetCode",
        "Array",
        "Medium",
        "Unsolved",
        1,
        30,
        "Not Started",
        None,
        "Kadane's algorithm",
    ),
    ProblemSeed(
        "Valid Anagram",
        "HackerRank",
        "String",
        "Easy",
        "Solved",
        1,
        15,
        "Mastered",
        0,
        "frequency counting",
    ),
    ProblemSeed(
        "Longest Common Prefix",
        "CodeChef",
        "String",
        "Easy",
        "Solved",
        1,
        20,
        "Second Revision",
        2,
        "prefix comparison",
    ),
    ProblemSeed(
        "Valid Palindrome",
        "GeeksforGeeks",
        "String",
        "Easy",
        "Solved",
        2,
        20,
        "Mastered",
        4,
        "two-pointer filtering",
    ),
    ProblemSeed(
        "First Unique Character in a String",
        "LeetCode",
        "String",
        "Easy",
        "Unsolved",
        2,
        25,
        "Not Started",
        None,
        "character frequency mapping",
    ),
    ProblemSeed(
        "Reverse Linked List",
        "HackerRank",
        "Linked List",
        "Easy",
        "Solved",
        1,
        20,
        "Mastered",
        1,
        "iterative pointer reversal",
    ),
    ProblemSeed(
        "Merge Two Sorted Lists",
        "CodeChef",
        "Linked List",
        "Easy",
        "Solved",
        2,
        30,
        "First Revision",
        3,
        "dummy-node merge",
    ),
    ProblemSeed(
        "Palindrome Linked List",
        "GeeksforGeeks",
        "Linked List",
        "Easy",
        "Revision Needed",
        2,
        35,
        "First Revision",
        None,
        "fast-slow pointers and reversal",
    ),
    ProblemSeed(
        "Valid Parentheses",
        "LeetCode",
        "Stack",
        "Easy",
        "Solved",
        1,
        20,
        "Mastered",
        1,
        "stack-based bracket matching",
    ),
    ProblemSeed(
        "Min Stack",
        "HackerRank",
        "Stack",
        "Medium",
        "Solved",
        2,
        35,
        "Second Revision",
        4,
        "auxiliary minimum tracking",
    ),
    ProblemSeed(
        "Largest Rectangle in Histogram",
        "CodeChef",
        "Stack",
        "Hard",
        "Unsolved",
        3,
        70,
        "Not Started",
        None,
        "monotonic stack",
    ),
    ProblemSeed(
        "Implement Queue using Stacks",
        "GeeksforGeeks",
        "Queue",
        "Easy",
        "Solved",
        2,
        30,
        "First Revision",
        5,
        "two-stack amortized operations",
    ),
    ProblemSeed(
        "Sliding Window Maximum",
        "LeetCode",
        "Queue",
        "Hard",
        "Unsolved",
        3,
        75,
        "Not Started",
        None,
        "monotonic deque",
    ),
    ProblemSeed(
        "Maximum Depth of Binary Tree",
        "HackerRank",
        "Tree",
        "Easy",
        "Solved",
        1,
        20,
        "Mastered",
        5,
        "recursive depth-first traversal",
    ),
    ProblemSeed(
        "Binary Tree Level Order Traversal",
        "CodeChef",
        "Tree",
        "Medium",
        "Solved",
        2,
        40,
        "First Revision",
        6,
        "breadth-first traversal",
    ),
    ProblemSeed(
        "Validate Binary Search Tree",
        "GeeksforGeeks",
        "Tree",
        "Medium",
        "Solved",
        2,
        45,
        "Mastered",
        10,
        "range-based recursive validation",
    ),
    ProblemSeed(
        "Binary Tree Maximum Path Sum",
        "LeetCode",
        "Tree",
        "Hard",
        "Revision Needed",
        3,
        80,
        "Second Revision",
        None,
        "post-order dynamic programming",
    ),
    ProblemSeed(
        "Number of Islands",
        "HackerRank",
        "Graph",
        "Medium",
        "Solved",
        2,
        45,
        "First Revision",
        6,
        "grid depth-first search",
    ),
    ProblemSeed(
        "Clone Graph",
        "CodeChef",
        "Graph",
        "Medium",
        "Solved",
        2,
        50,
        "Second Revision",
        12,
        "graph traversal with node mapping",
    ),
    ProblemSeed(
        "Course Schedule",
        "GeeksforGeeks",
        "Graph",
        "Medium",
        "Unsolved",
        3,
        55,
        "Not Started",
        None,
        "topological sorting",
    ),
    ProblemSeed(
        "Word Ladder",
        "LeetCode",
        "Graph",
        "Hard",
        "Revision Needed",
        4,
        85,
        "First Revision",
        None,
        "breadth-first search over transformations",
    ),
    ProblemSeed(
        "Climbing Stairs",
        "HackerRank",
        "Dynamic Programming",
        "Easy",
        "Solved",
        3,
        30,
        "First Revision",
        14,
        "one-dimensional state transition",
    ),
    ProblemSeed(
        "House Robber",
        "CodeChef",
        "Dynamic Programming",
        "Medium",
        "Unsolved",
        3,
        45,
        "Not Started",
        None,
        "include-exclude state transition",
    ),
    ProblemSeed(
        "Coin Change",
        "GeeksforGeeks",
        "Dynamic Programming",
        "Medium",
        "Revision Needed",
        4,
        65,
        "First Revision",
        None,
        "minimum-coin bottom-up table",
    ),
    ProblemSeed(
        "Longest Increasing Subsequence",
        "LeetCode",
        "Dynamic Programming",
        "Medium",
        "Unsolved",
        4,
        70,
        "Not Started",
        None,
        "subsequence state optimization",
    ),
    ProblemSeed(
        "Edit Distance",
        "HackerRank",
        "Dynamic Programming",
        "Hard",
        "Revision Needed",
        5,
        90,
        "Second Revision",
        None,
        "two-dimensional transition table",
    ),
    ProblemSeed(
        "Assign Cookies",
        "CodeChef",
        "Greedy",
        "Easy",
        "Solved",
        1,
        20,
        "Mastered",
        16,
        "sorted two-pointer matching",
    ),
    ProblemSeed(
        "Jump Game",
        "GeeksforGeeks",
        "Greedy",
        "Medium",
        "Solved",
        2,
        35,
        "First Revision",
        18,
        "maximum reachable index",
    ),
    ProblemSeed(
        "Gas Station",
        "LeetCode",
        "Greedy",
        "Medium",
        "Unsolved",
        2,
        45,
        "Not Started",
        None,
        "net-fuel greedy reset",
    ),
    ProblemSeed(
        "Binary Search",
        "HackerRank",
        "Binary Search",
        "Easy",
        "Solved",
        1,
        15,
        "Mastered",
        20,
        "iterative search bounds",
    ),
    ProblemSeed(
        "Search in Rotated Sorted Array",
        "CodeChef",
        "Binary Search",
        "Medium",
        "Solved",
        2,
        45,
        "Second Revision",
        22,
        "sorted-half detection",
    ),
    ProblemSeed(
        "Median of Two Sorted Arrays",
        "GeeksforGeeks",
        "Binary Search",
        "Hard",
        "Unsolved",
        3,
        85,
        "Not Started",
        None,
        "partition-based binary search",
    ),
    ProblemSeed(
        "Ransom Note",
        "LeetCode",
        "Hashing",
        "Easy",
        "Solved",
        1,
        15,
        "Mastered",
        24,
        "frequency subtraction",
    ),
    ProblemSeed(
        "Group Anagrams",
        "HackerRank",
        "Hashing",
        "Medium",
        "Solved",
        2,
        40,
        "First Revision",
        26,
        "canonical frequency keys",
    ),
    ProblemSeed(
        "Top K Frequent Elements",
        "CodeChef",
        "Hashing",
        "Medium",
        "Solved",
        2,
        45,
        "Second Revision",
        28,
        "frequency map with bucket grouping",
    ),
    ProblemSeed(
        "Longest Consecutive Sequence",
        "GeeksforGeeks",
        "Hashing",
        "Hard",
        "Revision Needed",
        3,
        70,
        "First Revision",
        None,
        "set-based sequence starts",
    ),
]


TARGET_COUNTS_BY_DAYS_AGO = {
    0: 4,
    1: 3,
    2: 4,
    3: 3,
    4: 2,
    5: 3,
    6: 3,
}


def slugify(value):
    """Convert a title into a URL-friendly slug."""

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)

    return value.strip("-")


def build_platform_link(platform, title):
    """Create a suitable sample platform link."""

    slug = slugify(title)

    if platform == "LeetCode":
        return f"https://leetcode.com/problems/{slug}/"

    if platform == "HackerRank":
        return (
            f"https://www.hackerrank.com/challenges/"
            f"{slug}/problem"
        )

    if platform == "CodeChef":
        return "https://www.codechef.com/practice"

    if platform == "GeeksforGeeks":
        return (
            f"https://www.geeksforgeeks.org/problems/"
            f"{slug}/1"
        )

    return None


def build_notes(status, focus):
    """Create meaningful notes based on the problem status."""

    if status == "Solved":
        return (
            f"Solved using {focus}. Review the approach and "
            f"time complexity during the next revision."
        )

    if status == "Revision Needed":
        return (
            f"Revise {focus}. Focus on edge cases, complexity, "
            f"and implementing the solution without hints."
        )

    return (
        f"Pending problem. Study {focus}, write a basic solution, "
        f"and then optimize it."
    )


def validate_sample_data():
    """Validate the required sample-data distributions."""

    if len(SAMPLE_PROBLEMS) != 40:
        raise ValueError(
            "Seed data must contain exactly 40 coding problems."
        )

    difficulty_counts = Counter(
        problem.difficulty
        for problem in SAMPLE_PROBLEMS
    )

    expected_difficulties = {
        "Easy": 18,
        "Medium": 15,
        "Hard": 7,
    }

    if difficulty_counts != expected_difficulties:
        raise ValueError(
            "Difficulty distribution is incorrect. "
            f"Expected {expected_difficulties}, "
            f"received {dict(difficulty_counts)}."
        )

    allowed_statuses = {
        "Solved",
        "Unsolved",
        "Revision Needed",
    }

    allowed_revision_statuses = {
        "Not Started",
        "First Revision",
        "Second Revision",
        "Mastered",
    }

    for problem in SAMPLE_PROBLEMS:
        if problem.status not in allowed_statuses:
            raise ValueError(
                f"Invalid status for {problem.title}."
            )

        if (
            problem.revision_status
            not in allowed_revision_statuses
        ):
            raise ValueError(
                f"Invalid revision status for {problem.title}."
            )

        if (
            problem.status == "Solved"
            and problem.solved_days_ago is None
        ):
            raise ValueError(
                f"Solved problem {problem.title} requires a date."
            )

        if (
            problem.status != "Solved"
            and problem.solved_days_ago is not None
        ):
            raise ValueError(
                f"Non-solved problem {problem.title} "
                f"must not contain a solved date."
            )


def get_or_create_role(name, description):
    """Return an existing role or create it."""

    role = Role.query.filter_by(name=name).first()

    if role is None:
        role = Role(
            name=name,
            description=description,
        )
        db.session.add(role)
        db.session.flush()

    return role


def get_or_create_demo_user(user_role):
    """Create or update the demo student account."""

    user = User.query.filter_by(
        email=DEMO_EMAIL
    ).first()

    if user is None:
        user = User(
            email=DEMO_EMAIL,
            password=hash_password(DEMO_PASSWORD),
            active=True,
            fs_uniquifier=uuid4().hex,
        )

        user.roles.append(user_role)

        db.session.add(user)
        db.session.flush()

        return user

    # Reset the password so the documented login always works.
    user.password = hash_password(DEMO_PASSWORD)
    user.active = True

    if not user.fs_uniquifier:
        user.fs_uniquifier = uuid4().hex

    if user_role not in user.roles:
        user.roles.append(user_role)

    db.session.flush()

    return user


def clear_existing_demo_data(user):
    """
    Remove only the demo user's sample records.

    Other users and their data are not changed.
    """

    DailyTarget.query.filter_by(
        user_id=user.id
    ).delete(
        synchronize_session=False
    )

    CodingProblem.query.filter_by(
        user_id=user.id
    ).delete(
        synchronize_session=False
    )

    db.session.flush()


def create_sample_problems(user):
    """Create the 40 coding problems for the demo user."""

    today = date.today()
    created_problems = []

    for item in SAMPLE_PROBLEMS:
        solved_date = None

        if item.status == "Solved":
            solved_date = today - timedelta(
                days=item.solved_days_ago
            )

        problem = CodingProblem(
            user_id=user.id,
            title=item.title,
            platform=item.platform,
            platform_link=build_platform_link(
                item.platform,
                item.title,
            ),
            topic=item.topic,
            difficulty=item.difficulty,
            status=item.status,
            attempts=item.attempts,
            time_spent_minutes=item.time_spent_minutes,
            revision_status=item.revision_status,
            notes=build_notes(
                item.status,
                item.focus,
            ),
            solved_date=solved_date,
        )

        created_problems.append(problem)

    db.session.add_all(created_problems)
    db.session.flush()

    return created_problems


def create_daily_targets(user, problems):
    """Create daily targets for today and the previous six days."""

    today = date.today()
    daily_targets = []

    for days_ago in range(6, -1, -1):
        target_date = today - timedelta(days=days_ago)

        solved_count = sum(
            1
            for problem in problems
            if (
                problem.status == "Solved"
                and problem.solved_date == target_date
            )
        )

        daily_target = DailyTarget(
            user_id=user.id,
            target_date=target_date,
            target_count=TARGET_COUNTS_BY_DAYS_AGO[
                days_ago
            ],
            solved_count=solved_count,
        )

        daily_targets.append(daily_target)

    db.session.add_all(daily_targets)
    db.session.flush()

    return daily_targets


def print_seed_summary(problems, targets):
    """Print a summary of the inserted demo data."""

    difficulty_counts = Counter(
        problem.difficulty
        for problem in problems
    )

    status_counts = Counter(
        problem.status
        for problem in problems
    )

    platform_counts = Counter(
        problem.platform
        for problem in problems
    )

    solved_last_7_days = sum(
        target.solved_count
        for target in targets
    )

    print("")
    print("=" * 58)
    print("CODING PERFORMANCE ANALYTICS DASHBOARD SEED COMPLETE")
    print("=" * 58)
    print(f"Demo email:    {DEMO_EMAIL}")
    print(f"Demo password: {DEMO_PASSWORD}")
    print("")
    print(f"Coding problems created: {len(problems)}")
    print(f"Daily targets created:   {len(targets)}")
    print("")
    print("Difficulty distribution:")
    print(f"  Easy:   {difficulty_counts['Easy']}")
    print(f"  Medium: {difficulty_counts['Medium']}")
    print(f"  Hard:   {difficulty_counts['Hard']}")
    print("")
    print("Status distribution:")
    print(f"  Solved:          {status_counts['Solved']}")
    print(f"  Unsolved:        {status_counts['Unsolved']}")
    print(
        "  Revision Needed: "
        f"{status_counts['Revision Needed']}"
    )
    print("")
    print("Platform distribution:")

    for platform in sorted(platform_counts):
        print(
            f"  {platform}: "
            f"{platform_counts[platform]}"
        )

    print("")
    print(
        "Solved problems in the last 7 days: "
        f"{solved_last_7_days}"
    )
    print("")
    print("Analytics characteristics:")
    print("  Dynamic Programming: weak progress")
    print("  Graph: medium progress")
    print("  Array: strong progress")
    print("  String: strong progress")
    print("=" * 58)
    print("")


def seed_database():
    """Seed roles, demo user, problems, and daily targets."""

    validate_sample_data()

    admin_role = get_or_create_role(
        name="admin",
        description=(
            "Administrator with access to application "
            "management features."
        ),
    )

    user_role = get_or_create_role(
        name="user",
        description=(
            "Student user who tracks coding practice "
            "and performance."
        ),
    )

    demo_user = get_or_create_demo_user(user_role)

    clear_existing_demo_data(demo_user)

    problems = create_sample_problems(demo_user)
    targets = create_daily_targets(
        demo_user,
        problems,
    )

    db.session.commit()

    print_seed_summary(
        problems,
        targets,
    )

    # Keep references explicit so both required roles are created.
    _ = admin_role


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        try:
            seed_database()

        except Exception as error:
            db.session.rollback()

            print("")
            print("SEEDING FAILED")
            print(f"Reason: {error}")
            print("")

            raise