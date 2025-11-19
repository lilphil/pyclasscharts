"""Base client for ClassCharts API."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, cast

import requests

from pyclasscharts.consts import PING_INTERVAL
from pyclasscharts.exceptions import APIError, NoSessionError
from pyclasscharts.types import (
    ActivityPoint,
    ActivityResponse,
    AnnouncementsResponse,
    AttendanceResponse,
    BadgesResponse,
    BehaviourResponse,
    DetentionsResponse,
    GetActivityOptions,
    GetAttendanceOptions,
    GetBehaviourOptions,
    GetFullActivityOptions,
    GetHomeworkOptions,
    GetLessonsOptions,
    GetStudentInfoResponse,
    HomeworksResponse,
    LessonsResponse,
    PupilFieldsResponse,
)


class BaseClient(ABC):
    """
    Shared client for both parent and student.

    This is an abstract base class and should not be used directly.
    """

    def __init__(self, api_base: str) -> None:
        """
        Create a new client with the given API URL.

        Args:
            api_base: Base API URL, different for parent vs student
        """
        self.student_id: int = 0
        self.auth_cookies: List[str] = []
        self.session_id: str = ""
        self.last_ping: float = 0.0
        self._api_base = api_base
        self._session = requests.Session()
        self._session.headers.update(
            {"User-Agent": "classcharts-api https://github.com/classchartsapi/classcharts-api-py"}
        )

    @abstractmethod
    def login(self) -> None:
        """Authenticate with ClassCharts. Must be implemented by subclasses."""
        pass

    def get_new_session_id(self) -> None:
        """
        Revalidate the session ID.

        This is called automatically when the session ID is older than 3 minutes
        and initially using the .login() method.
        """
        form_data = {"include_data": "true"}
        ping_data = self._make_authed_request(
            f"{self._api_base}/ping",
            method="POST",
            data=form_data,
            revalidate_token=False,
        )
        self.session_id = ping_data["meta"]["session_id"]
        self.last_ping = time.time() * 1000  # Convert to milliseconds

    def _make_authed_request(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        revalidate_token: bool = True,
    ) -> Dict[str, Any]:
        """
        Make a request to the ClassCharts API with required authentication headers.

        Args:
            path: Path to the API endpoint
            method: HTTP method (GET, POST, etc.)
            data: Form data to send (dict for form-encoded, str for raw body)
            json_data: JSON data to send
            params: URL parameters
            headers: Additional headers to include in the request
            revalidate_token: Whether to revalidate the session ID if it's older than 3 minutes

        Returns:
            Response JSON as a dictionary

        Raises:
            NoSessionError: If no session ID is available
            APIError: If the API returns an error response
        """
        if not self.session_id:
            raise NoSessionError("No session ID")

        # Revalidate token if needed
        if revalidate_token and self.last_ping:
            current_time = time.time() * 1000  # Convert to milliseconds
            if current_time - self.last_ping + 5000 > PING_INTERVAL:
                self.get_new_session_id()

        # Prepare headers
        request_headers: Dict[str, str] = {
            "Authorization": f"Basic {self.session_id}",
        }

        # Add cookies if available
        if self.auth_cookies:
            request_headers["Cookie"] = "; ".join(self.auth_cookies)

        # Merge with any additional headers
        if headers:
            request_headers.update(headers)

        # Make the request
        response = self._session.request(
            method=method,
            url=path,
            headers=request_headers,
            data=data,
            json=json_data,
            params=params,
        )

        # Parse response
        try:
            response_json: Dict[str, Any] = response.json()
        except json.JSONDecodeError as e:
            raise APIError(f"Error parsing JSON. Returned response: {response.text}") from e

        if response_json.get("success") == 0:
            error_msg = response_json.get("error", "Unknown error")
            raise APIError(error_msg)

        return response_json

    def get_student_info(self) -> GetStudentInfoResponse:
        """
        Get general information about the current student.

        Returns:
            Student information response
        """
        body = {"include_data": "true"}
        return cast(
            GetStudentInfoResponse,
            self._make_authed_request(
                f"{self._api_base}/ping",
                method="POST",
                data=body,
            ),
        )

    def get_activity(
        self,
        options: Optional[GetActivityOptions] = None,
    ) -> ActivityResponse:
        """
        Get the current student's activity.

        This function is only used for pagination. You likely want get_full_activity().

        Args:
            options: Options for getting activity data

        Returns:
            Activity data response

        See Also:
            get_full_activity: Gets all activity data between two dates
        """
        params: Dict[str, str] = {}
        if options:
            if "from_date" in options:
                params["from"] = options["from_date"]
            if "to_date" in options:
                params["to"] = options["to_date"]
            if "last_id" in options:
                params["last_id"] = options["last_id"]

        return cast(
            ActivityResponse,
            self._make_authed_request(
                f"{self._api_base}/activity/{self.student_id}",
                method="GET",
                params=params,
            ),
        )

    def get_full_activity(
        self,
        options: GetFullActivityOptions,
    ) -> List[ActivityPoint]:
        """
        Get the current student's activity between two dates.

        This function will automatically paginate through all the data returned by get_activity().

        Args:
            options: Options for getting full activity data

        Returns:
            List of activity points

        See Also:
            get_activity: Gets a single page of activity data
        """
        data: List[ActivityPoint] = []
        prev_last: Optional[int] = None
        got_data = True

        while got_data:
            params: GetActivityOptions = {
                "from_date": options["from_date"],
                "to_date": options["to_date"],
            }
            if prev_last is not None:
                params["last_id"] = str(prev_last)

            fragment = self.get_activity(params)["data"]
            if not fragment or not len(fragment):
                got_data = False
            else:
                data.extend(fragment)
                prev_last = fragment[-1]["id"]

        return data

    def get_behaviour(
        self,
        options: Optional[GetBehaviourOptions] = None,
    ) -> BehaviourResponse:
        """
        Get the current student's behaviour.

        Args:
            options: Options for getting behaviour data

        Returns:
            Behaviour response
        """
        params: Dict[str, str] = {}
        if options:
            if "from_date" in options:
                params["from"] = options["from_date"]
            if "to_date" in options:
                params["to"] = options["to_date"]

        return cast(
            BehaviourResponse,
            self._make_authed_request(
                f"{self._api_base}/behaviour/{self.student_id}",
                method="GET",
                params=params,
            ),
        )

    def get_homeworks(
        self,
        options: Optional[GetHomeworkOptions] = None,
    ) -> HomeworksResponse:
        """
        Get the current student's homework.

        Args:
            options: Options for getting homework data

        Returns:
            Homeworks response
        """
        params: Dict[str, Any] = {}
        if options:
            if "display_date" in options:
                params["display_date"] = options["display_date"]
            if "from_date" in options:
                params["from"] = options["from_date"]
            if "to_date" in options:
                params["to"] = options["to_date"]

        return cast(
            HomeworksResponse,
            self._make_authed_request(
                f"{self._api_base}/homeworks/{self.student_id}",
                method="GET",
                params=params,
            ),
        )

    def get_lessons(
        self,
        options: GetLessonsOptions,
    ) -> LessonsResponse:
        """
        Get the current student's lessons for a given date.

        Args:
            options: Options for getting lessons data (must include date)

        Returns:
            Lessons response

        Raises:
            ValueError: If no date is specified
        """
        if not options or "date" not in options:
            raise ValueError("No date specified")

        params = {"date": options["date"]}
        return cast(
            LessonsResponse,
            self._make_authed_request(
                f"{self._api_base}/timetable/{self.student_id}",
                method="GET",
                params=params,
            ),
        )

    def get_badges(self) -> BadgesResponse:
        """
        Get the current student's earned badges.

        Returns:
            Badges response
        """
        return cast(
            BadgesResponse,
            self._make_authed_request(
                f"{self._api_base}/eventbadges/{self.student_id}",
                method="GET",
            ),
        )

    def get_announcements(self) -> AnnouncementsResponse:
        """
        Get the current student's announcements.

        Returns:
            Announcements response
        """
        return cast(
            AnnouncementsResponse,
            self._make_authed_request(
                f"{self._api_base}/announcements/{self.student_id}",
                method="GET",
            ),
        )

    def get_detentions(self) -> DetentionsResponse:
        """
        Get the current student's detentions.

        Returns:
            Detentions response
        """
        return cast(
            DetentionsResponse,
            self._make_authed_request(
                f"{self._api_base}/detentions/{self.student_id}",
                method="GET",
            ),
        )

    def get_attendance(
        self,
        options: Optional[GetAttendanceOptions] = None,
    ) -> AttendanceResponse:
        """
        Get the current student's attendance.

        Args:
            options: Options for getting attendance data

        Returns:
            Attendance response
        """
        params: Dict[str, str] = {}
        if options:
            if "from_date" in options:
                params["from"] = options["from_date"]
            if "to_date" in options:
                params["to"] = options["to_date"]

        return cast(
            AttendanceResponse,
            self._make_authed_request(
                f"{self._api_base}/attendance/{self.student_id}",
                method="GET",
                params=params,
            ),
        )

    def get_pupil_fields(self) -> PupilFieldsResponse:
        """
        Get the current student's pupil fields.

        Returns:
            Pupil fields response
        """
        return cast(
            PupilFieldsResponse,
            self._make_authed_request(
                f"{self._api_base}/customfields/{self.student_id}",
                method="GET",
            ),
        )
