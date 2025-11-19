"""Student client for ClassCharts API."""

import json
from typing import cast

import requests

from pyclasscharts.base_client import BaseClient
from pyclasscharts.consts import API_BASE_STUDENT, BASE_URL
from pyclasscharts.exceptions import AuthenticationError, ValidationError
from pyclasscharts.types import (
    GetStudentCodeOptions,
    GetStudentCodeResponse,
    RewardPurchaseResponse,
    RewardsResponse,
)
from pyclasscharts.utils import parse_cookies


class StudentClient(BaseClient):
    """
    Student Client.

    See BaseClient for all shared methods.

    Example:
        >>> from pyclasscharts import StudentClient
        >>> # Date of birth MUST be in the format DD/MM/YYYY
        >>> client = StudentClient("classchartsCode", "01/01/2000")
        >>> client.login()
    """

    def __init__(self, student_code: str, date_of_birth: str = "") -> None:
        """
        Initialize a student client.

        Args:
            student_code: ClassCharts student code
            date_of_birth: Student's date of birth (format: DD/MM/YYYY)
        """
        super().__init__(API_BASE_STUDENT)
        self.student_code = str(student_code)
        self.date_of_birth = str(date_of_birth)

    def login(self) -> None:
        """
        Authenticate with ClassCharts.

        Raises:
            ValidationError: If student code is not provided
            AuthenticationError: If authentication fails
        """
        if not self.student_code:
            raise ValidationError("Student Code not provided")

        form_data = {
            "_method": "POST",
            "code": self.student_code.upper(),
            "dob": self.date_of_birth,
            "remember_me": "1",
            "recaptcha-token": "no-token-available",
        }

        response = requests.post(
            f"{BASE_URL}/student/login",
            data=form_data,
            allow_redirects=False,
        )

        if response.status_code != 302 or "set-cookie" not in response.headers:
            raise AuthenticationError(
                "Unauthenticated: ClassCharts didn't return authentication cookies"
            )

        cookies = response.headers.get("set-cookie", "")
        self.auth_cookies = cookies.split(",")
        session_cookies = parse_cookies(cookies)
        session_credentials = session_cookies.get("student_session_credentials", "")

        if not session_credentials:
            raise AuthenticationError("Failed to extract session credentials")

        try:
            session_id_data = json.loads(session_credentials)
            self.session_id = session_id_data["session_id"]
        except (json.JSONDecodeError, KeyError) as e:
            raise AuthenticationError("Failed to parse session credentials") from e

        self.get_new_session_id()
        user = self.get_student_info()
        self.student_id = user["data"]["user"]["id"]

    def get_rewards(self) -> RewardsResponse:
        """
        Get the available items in the current student's rewards shop.

        Returns:
            Array of purchasable items
        """
        return cast(
            RewardsResponse,
            self._make_authed_request(
                f"{self._api_base}/rewards/{self.student_id}",
                method="GET",
            ),
        )

    def purchase_reward(self, item_id: int) -> RewardPurchaseResponse:
        """
        Purchase a reward item from the current student's rewards shop.

        Args:
            item_id: ID of the reward item to purchase

        Returns:
            An object containing the current student's balance and item ID purchased
        """
        body = f"pupil_id={self.student_id}"
        return cast(
            RewardPurchaseResponse,
            self._make_authed_request(
                f"{self._api_base}/purchase/{item_id}",
                method="POST",
                data=body,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            ),
        )

    def get_student_code(
        self,
        options: GetStudentCodeOptions,
    ) -> GetStudentCodeResponse:
        """
        Get the current student's student code.

        Args:
            options: Options containing date_of_birth in format YYYY-MM-DD

        Returns:
            Response containing the student code
        """
        return cast(
            GetStudentCodeResponse,
            self._make_authed_request(
                f"{self._api_base}/getcode",
                method="POST",
                data=f"date={options['date_of_birth']}",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                },
            ),
        )
