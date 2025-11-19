#!/usr/bin/env python3
"""Test script for ClassCharts API authentication and timetable fetching."""

import argparse
import sys
from datetime import datetime, timedelta

from pyclasscharts import ParentClient, StudentClient
from pyclasscharts.exceptions import AuthenticationError, ValidationError


def test_parent_auth(email: str, password: str, date: str | None = None) -> None:
    """Test parent authentication and fetch timetable."""
    print("=" * 60)
    print("Testing Parent Client Authentication")
    print("=" * 60)

    try:
        client = ParentClient(email, password)
        print(f"✓ Created ParentClient for: {email}")

        print("\nAttempting login...")
        client.login()
        print("✓ Login successful!")

        # Get pupils
        pupils = client.get_pupils()
        print(f"\n✓ Found {len(pupils)} pupil(s):")
        for pupil in pupils:
            print(f"  - {pupil['name']} (ID: {pupil['id']})")

        # Select first pupil if multiple
        if len(pupils) > 0:
            client.select_pupil(pupils[0]["id"])
            print(f"\n✓ Selected pupil: {pupils[0]['name']}")

            # Get student info
            student_info = client.get_student_info()
            print(f"✓ Student info retrieved: {student_info['data']['user']['name']}")

            # Get timetable
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            print(f"\nFetching timetable for: {date}")
            lessons = client.get_lessons(options={"date": date})

            print_timetable(lessons, date)

    except ValidationError as e:
        print(f"✗ Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AuthenticationError as e:
        print(f"✗ Authentication Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_student_auth(student_code: str, date_of_birth: str, date: str | None = None) -> None:
    """Test student authentication and fetch timetable."""
    print("=" * 60)
    print("Testing Student Client Authentication")
    print("=" * 60)

    try:
        client = StudentClient(student_code, date_of_birth)
        print(f"✓ Created StudentClient for code: {student_code}")

        print("\nAttempting login...")
        client.login()
        print("✓ Login successful!")

        # Get student info
        student_info = client.get_student_info()
        print(f"✓ Student info retrieved: {student_info['data']['user']['name']}")

        # Get timetable
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        print(f"\nFetching timetable for: {date}")
        lessons = client.get_lessons(options={"date": date})

        print_timetable(lessons, date)

    except ValidationError as e:
        print(f"✗ Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AuthenticationError as e:
        print(f"✗ Authentication Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def print_timetable(lessons: dict, date: str) -> None:
    """Print timetable in a readable format."""
    print("\n" + "=" * 60)
    print(f"Timetable for {date}")
    print("=" * 60)

    if not lessons.get("data"):
        print("No lessons found for this date.")
        return

    lesson_list = lessons["data"]
    meta = lessons.get("meta", {})

    if meta:
        print(f"\nSchool day: {meta.get('start_time', 'N/A')} - {meta.get('end_time', 'N/A')}")
        if meta.get("periods"):
            print(f"Periods: {len(meta['periods'])}")

    print(f"\nTotal lessons: {len(lesson_list)}\n")

    # Group by period if available
    for lesson in lesson_list:
        period = lesson.get("period_name", "N/A")
        start_time = lesson.get("start_time", "N/A")
        end_time = lesson.get("end_time", "N/A")
        subject = lesson.get("subject_name", "N/A")
        lesson_name = lesson.get("lesson_name", "N/A")
        teacher = lesson.get("teacher_name", "N/A")
        room = lesson.get("room_name", "N/A")

        print(f"Period {period}: {start_time} - {end_time}")
        print(f"  Subject: {subject}")
        print(f"  Lesson: {lesson_name}")
        print(f"  Teacher: {teacher}")
        print(f"  Room: {room}")

        if lesson.get("note"):
            print(f"  Note: {lesson['note']}")

        if lesson.get("pupil_note"):
            print(f"  Your Note: {lesson['pupil_note']}")

        print()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test ClassCharts API authentication and fetch timetable"
    )
    parser.add_argument(
        "--type",
        choices=["parent", "student"],
        required=True,
        help="Authentication type: parent or student",
    )
    parser.add_argument(
        "--email",
        help="Parent email (required for parent type)",
    )
    parser.add_argument(
        "--password",
        help="Parent password (required for parent type)",
    )
    parser.add_argument(
        "--student-code",
        dest="student_code",
        help="Student code (required for student type)",
    )
    parser.add_argument(
        "--date-of-birth",
        dest="date_of_birth",
        help="Student date of birth in DD/MM/YYYY format (required for student type)",
    )
    parser.add_argument(
        "--date",
        help="Date to fetch timetable for (YYYY-MM-DD format, defaults to today)",
    )

    args = parser.parse_args()

    if args.type == "parent":
        if not args.email or not args.password:
            print("Error: --email and --password are required for parent authentication", file=sys.stderr)
            sys.exit(1)
        test_parent_auth(args.email, args.password, args.date)
    elif args.type == "student":
        if not args.student_code or not args.date_of_birth:
            print(
                "Error: --student-code and --date-of-birth are required for student authentication",
                file=sys.stderr,
            )
            sys.exit(1)
        test_student_auth(args.student_code, args.date_of_birth, args.date)

    print("\n" + "=" * 60)
    print("✓ Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

