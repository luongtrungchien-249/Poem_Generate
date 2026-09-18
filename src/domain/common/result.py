from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeGuard, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    error: E


Result: TypeAlias = Ok[T] | Err[E]


def is_ok(res: Result[T, E]) -> TypeGuard[Ok[T]]:
    return isinstance(res, Ok)


def is_err(res: Result[T, E]) -> TypeGuard[Err[E]]:
    return isinstance(res, Err)
