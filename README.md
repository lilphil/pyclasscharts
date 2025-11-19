# pyclasscharts

A Python client library for the ClassCharts API, providing easy access to student and parent data from ClassCharts.

## Features

- 🔐 **Authentication**: Support for both parent and student login
- 📚 **Comprehensive API**: Access to homework, behaviour, attendance, lessons, and more
- 🎯 **Type Safety**: Full type hints using TypedDict for better IDE support
- 🧪 **Well Tested**: Comprehensive test suite with pytest
- 🐍 **Pythonic**: Idiomatic Python code following best practices

## Installation

### From GitHub

```bash
pip install git+https://github.com/lilphil/pyclasscharts.git
```

## Quick Start

### Parent Client

```python
from pyclasscharts import ParentClient

# Create a client with your email and password
client = ParentClient("your.email@example.com", "your_password")

# Login
client.login()

# Get list of pupils
pupils = client.get_pupils()
print(f"Found {len(pupils)} pupils")

# Select a pupil (defaults to first pupil)
client.select_pupil(pupils[0]["id"])

# Get student information
student_info = client.get_student_info()
print(f"Student: {student_info['data']['user']['name']}")

# Get homework
homework = client.get_homeworks()
print(f"Found {len(homework['data'])} homework assignments")

# Get behaviour data
behaviour = client.get_behaviour()
print(f"Behaviour timeline: {len(behaviour['data']['timeline'])} points")

# Get attendance
attendance = client.get_attendance(
    options={"from_date": "2024-01-01", "to_date": "2024-01-31"}
)
print(f"Attendance percentage: {attendance['meta']['percentage']}%")
```

### Student Client

```python
from pyclasscharts import StudentClient

# Create a client with student code and date of birth
# Date of birth format: DD/MM/YYYY
client = StudentClient("ABC123", "01/01/2000")

# Login
client.login()

# Get student information
student_info = client.get_student_info()
print(f"Student: {student_info['data']['user']['name']}")

# Get homework
homework = client.get_homeworks()
print(f"Found {len(homework['data'])} homework assignments")

# Get lessons for a specific date
lessons = client.get_lessons(options={"date": "2024-01-15"})
print(f"Lessons on 2024-01-15: {len(lessons['data'])}")

# Get rewards shop
rewards = client.get_rewards()
print(f"Available rewards: {len(rewards['data'])}")

# Purchase a reward (if you have enough points)
if rewards['data'][0]['can_purchase']:
    purchase = client.purchase_reward(rewards['data'][0]['id'])
    print(f"New balance: {purchase['data']['balance']}")
```

## API Reference

### ParentClient

#### Methods

- `login()` - Authenticate with ClassCharts
- `get_pupils()` - Get list of pupils connected to the parent account
- `select_pupil(pupil_id: int)` - Select a pupil to use for API requests
- `change_password(current_password: str, new_password: str)` - Change parent account password
- `get_student_info()` - Get general information about the current student
- `get_homeworks(options?: GetHomeworkOptions)` - Get homework assignments
- `get_behaviour(options?: GetBehaviourOptions)` - Get behaviour data
- `get_attendance(options?: GetAttendanceOptions)` - Get attendance data
- `get_lessons(options: GetLessonsOptions)` - Get lessons for a specific date
- `get_activity(options?: GetActivityOptions)` - Get activity feed (paginated)
- `get_full_activity(options: GetFullActivityOptions)` - Get all activity between dates
- `get_badges()` - Get earned badges
- `get_announcements()` - Get announcements
- `get_detentions()` - Get detentions
- `get_pupil_fields()` - Get custom pupil fields

### StudentClient

#### Methods

- `login()` - Authenticate with ClassCharts
- `get_student_info()` - Get general information about the student
- `get_homeworks(options?: GetHomeworkOptions)` - Get homework assignments
- `get_behaviour(options?: GetBehaviourOptions)` - Get behaviour data
- `get_attendance(options?: GetAttendanceOptions)` - Get attendance data
- `get_lessons(options: GetLessonsOptions)` - Get lessons for a specific date
- `get_activity(options?: GetActivityOptions)` - Get activity feed (paginated)
- `get_full_activity(options: GetFullActivityOptions)` - Get all activity between dates
- `get_badges()` - Get earned badges
- `get_announcements()` - Get announcements
- `get_detentions()` - Get detentions
- `get_pupil_fields()` - Get custom pupil fields
- `get_rewards()` - Get available rewards in the shop
- `purchase_reward(item_id: int)` - Purchase a reward item
- `get_student_code(options: GetStudentCodeOptions)` - Get student code using date of birth

## Options Types

### GetHomeworkOptions
```python
{
    "display_date": "due_date" | "issue_date",  # Default: "issue_date"
    "from_date": "YYYY-MM-DD",  # Optional
    "to_date": "YYYY-MM-DD"    # Optional
}
```

### GetBehaviourOptions
```python
{
    "from_date": "YYYY-MM-DD",  # Optional
    "to_date": "YYYY-MM-DD"     # Optional
}
```

### GetAttendanceOptions
```python
{
    "from_date": "YYYY-MM-DD",  # Required
    "to_date": "YYYY-MM-DD"     # Required
}
```

### GetLessonsOptions
```python
{
    "date": "YYYY-MM-DD"  # Required
}
```

### GetFullActivityOptions
```python
{
    "from_date": "YYYY-MM-DD",  # Required
    "to_date": "YYYY-MM-DD"     # Required
}
```

### GetStudentCodeOptions
```python
{
    "date_of_birth": "YYYY-MM-DD"  # Required
}
```

## Error Handling

The library uses custom exceptions for error handling:

```python
from pyclasscharts.exceptions import (
    ClassChartsError,
    AuthenticationError,
    APIError,
    NoSessionError,
    ValidationError,
)

try:
    client.login()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Examples

### Get all homework due this week

```python
from datetime import datetime, timedelta
from pyclasscharts import ParentClient

client = ParentClient("email@example.com", "password")
client.login()

# Get homework due in the next 7 days
today = datetime.now()
next_week = today + timedelta(days=7)

homework = client.get_homeworks(
    options={
        "display_date": "due_date",
        "from_date": today.strftime("%Y-%m-%d"),
        "to_date": next_week.strftime("%Y-%m-%d"),
    }
)

for hw in homework["data"]:
    if hw["status"]["state"] != "completed":
        print(f"{hw['title']} - Due: {hw['due_date']}")
```

### Get behaviour summary

```python
from pyclasscharts import ParentClient

client = ParentClient("email@example.com", "password")
client.login()

behaviour = client.get_behaviour()

print("Positive reasons:")
for reason, count in behaviour["data"]["positive_reasons"].items():
    print(f"  {reason}: {count}")

print("\nNegative reasons:")
for reason, count in behaviour["data"]["negative_reasons"].items():
    print(f"  {reason}: {count}")
```

### Get full activity feed

```python
from pyclasscharts import ParentClient

client = ParentClient("email@example.com", "password")
client.login()

# Get all activity for the current month
activity = client.get_full_activity(
    options={
        "from_date": "2024-01-01",
        "to_date": "2024-01-31",
    }
)

print(f"Total activity points: {len(activity)}")
for point in activity[:10]:  # Show first 10
    print(f"{point['timestamp']}: {point['reason']} ({point['score']} points)")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pyclasscharts.git
cd pyclasscharts

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyclasscharts

# Run specific test file
pytest tests/test_parent_client.py
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy pyclasscharts
```

## Requirements

- Python 3.8+
- requests >= 2.28.0

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This library is a Python port of the [classcharts-api-js](https://github.com/classchartsapi/classcharts-api-js) library.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

