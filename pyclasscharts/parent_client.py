"""Parent client for ClassCharts API."""

import json
from typing import List, cast

import requests

from pyclasscharts.base_client import BaseClient
from pyclasscharts.consts import API_BASE_PARENT, BASE_URL
from pyclasscharts.exceptions import AuthenticationError, ValidationError
from pyclasscharts.types import ChangePasswordResponse, GetPupilsResponse, Pupil
from pyclasscharts.utils import parse_cookies


class ParentClient(BaseClient):
    """
    Parent Client.

    See BaseClient for all shared methods.

    Example:
        >>> from pyclasscharts import ParentClient
        >>> client = ParentClient("username", "password")
        >>> client.login()
        >>> pupils = client.get_pupils()
    """

    def __init__(self, email: str, password: str) -> None:
        """
        Initialize a parent client.

        Args:
            email: Parent's email address
            password: Parent's password
        """
        super().__init__(API_BASE_PARENT)
        self.email = str(email)
        self.password = str(password)
        self.pupils: List[Pupil] = []

    def login(self) -> None:
        """
        Authenticate with ClassCharts.

        Raises:
            ValidationError: If email or password is not provided
            AuthenticationError: If authentication fails
        """
        if not self.email:
            raise ValidationError("Email not provided")
        if not self.password:
            raise ValidationError("Password not provided")

        form_data = {
            "_method": "POST",
            "email": self.email,
            "logintype": "existing",
            "password": self.password,
            "recaptcha-token": "no-token-available",
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(
            f"{BASE_URL}/parent/login",
            data=form_data,
            headers=headers,
            allow_redirects=False,
        )

        if response.status_code != 302 or "set-cookie" not in response.headers:
            raise AuthenticationError(
                "Unauthenticated: ClassCharts didn't return authentication cookies"
            )

        cookies = response.headers.get("set-cookie", "")
        session_cookies = parse_cookies(cookies)
        session_credentials = session_cookies.get("parent_session_credentials", "")

        if not session_credentials:
            raise AuthenticationError("Failed to extract session credentials")

        try:
            session_id_data = json.loads(session_credentials)
            self.session_id = session_id_data["session_id"]
        except (json.JSONDecodeError, KeyError) as e:
            raise AuthenticationError("Failed to parse session credentials") from e

        self.pupils = self.get_pupils()
        if not self.pupils:
            raise ValidationError("Account has no pupils attached")

        self.student_id = self.pupils[0]["id"]

    def get_pupils(self) -> GetPupilsResponse:
        """
        Get a list of pupils connected to this parent's account.

        Returns:
            A list of pupils connected to this parent's account
        """
        response = self._make_authed_request(
            f"{self._api_base}/pupils",
            method="GET",
        )
        return cast(GetPupilsResponse, response["data"])

    def select_pupil(self, pupil_id: int) -> None:
        """
        Select a pupil to be used with API requests.

        Args:
            pupil_id: Pupil ID obtained from self.pupils or get_pupils()

        Raises:
            ValidationError: If no pupil ID is specified or pupil not found

        See Also:
            get_pupils: Get list of available pupils
        """
        if not pupil_id:
            raise ValidationError("No pupil ID specified")

        for pupil in self.pupils:
            if pupil["id"] == pupil_id:
                self.student_id = pupil["id"]
                return

        raise ValidationError("No pupil with specified ID found")

    def change_password(
        self,
        current_password: str,
        new_password: str,
    ) -> ChangePasswordResponse:
        """
        Change the login password for the current parent account.

        Args:
            current_password: Current password
            new_password: New password

        Returns:
            Whether the request was successful
        """
        form_data = {
            "current": current_password,
            "new": new_password,
            "repeat": new_password,
        }
        return cast(
            ChangePasswordResponse,
            self._make_authed_request(
                f"{self._api_base}/password",
                method="POST",
                data=form_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            ),
        )
