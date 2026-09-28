from typing import Any


class User:
    def __init__(self, user_id: int, name: str, username: str, email: str) -> None:
        self._id = user_id
        self._name = name
        self._username = username
        self._email = email

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "User":
        return cls(
            user_id=data["id"],
            name=data["name"],
            username=data["username"],
            email=data["email"],
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email