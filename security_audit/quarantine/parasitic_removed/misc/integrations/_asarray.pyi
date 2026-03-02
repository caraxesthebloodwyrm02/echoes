from collections.abc import Iterable
from typing import Any, Literal, TypeVar, overload

from numpy._typing import DTypeLike, NDArray, _SupportsArrayFunc

_ArrayT = TypeVar("_ArrayT", bound=NDArray[Any])

type _Requirements = Literal[
    "C",
    "C_CONTIGUOUS",
    "CONTIGUOUS",
    "F",
    "F_CONTIGUOUS",
    "FORTRAN",
    "A",
    "ALIGNED",
    "W",
    "WRITEABLE",
    "O",
    "OWNDATA",
]
type _E = Literal["E", "ENSUREARRAY"]
type _RequirementsWithE = _Requirements | _E

@overload
def require(
    a: _ArrayT,
    dtype: None = ...,
    requirements: _Requirements | Iterable[_Requirements] | None = ...,
    *,
    like: _SupportsArrayFunc = ...,
) -> _ArrayT: ...
@overload
def require(
    a: object,
    dtype: DTypeLike = ...,
    requirements: _E | Iterable[_RequirementsWithE] = ...,
    *,
    like: _SupportsArrayFunc = ...,
) -> NDArray[Any]: ...
@overload
def require(
    a: object,
    dtype: DTypeLike = ...,
    requirements: _Requirements | Iterable[_Requirements] | None = ...,
    *,
    like: _SupportsArrayFunc = ...,
) -> NDArray[Any]: ...
