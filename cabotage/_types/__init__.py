from typing import cast


class InvariantViolationError(Exception): ...


def assume_not_none[T](val: T | None, /, *, because: str) -> T:
    return cast("T", val)


def require_not_none[T](val: T | None, /, *, because: str) -> T:
    if val is None:
        raise InvariantViolationError(f"Invariant violated; assumption: {because}")
    return val
