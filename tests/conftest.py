import sys
from pathlib import Path
import hashlib
import hmac
import secrets
import types


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class InvalidEmailError(ValueError):
    pass


class WeakPasswordError(ValueError):
    pass


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserInactiveError(Exception):
    pass


class Email:
    def __init__(self, value: str):
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.split("@")[-1]:
            raise InvalidEmailError("Invalid email")
        self.value = normalized

    def __str__(self):
        return self.value


class Password:
    def __init__(self, hashed_value: str, salt: str):
        self.hashed_value = hashed_value
        self.salt = salt

    @classmethod
    def create(cls, plain: str):
        if len(plain) < 8:
            raise WeakPasswordError("Weak password")
        salt = secrets.token_hex(8)
        digest = hashlib.sha256(f"{salt}:{plain}".encode()).hexdigest()
        return cls(hashed_value=digest, salt=salt)

    @classmethod
    def from_hash(cls, hashed_value: str, salt: str):
        return cls(hashed_value=hashed_value, salt=salt)

    def verify(self, plain: str) -> bool:
        candidate = hashlib.sha256(f"{self.salt}:{plain}".encode()).hexdigest()
        return hmac.compare_digest(candidate, self.hashed_value)


video_processor_shared = types.ModuleType("video_processor_shared")
domain_mod = types.ModuleType("video_processor_shared.domain")
value_objects_mod = types.ModuleType("video_processor_shared.domain.value_objects")
exceptions_mod = types.ModuleType("video_processor_shared.domain.exceptions")

value_objects_mod.Email = Email
value_objects_mod.Password = Password

exceptions_mod.InvalidEmailError = InvalidEmailError
exceptions_mod.WeakPasswordError = WeakPasswordError
exceptions_mod.UserAlreadyExistsError = UserAlreadyExistsError
exceptions_mod.InvalidCredentialsError = InvalidCredentialsError
exceptions_mod.UserInactiveError = UserInactiveError

sys.modules.setdefault("video_processor_shared", video_processor_shared)
sys.modules.setdefault("video_processor_shared.domain", domain_mod)
sys.modules.setdefault("video_processor_shared.domain.value_objects", value_objects_mod)
sys.modules.setdefault("video_processor_shared.domain.exceptions", exceptions_mod)
