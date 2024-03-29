from typing import Any, Iterable, Iterator, TypeVar, Optional

T = TypeVar("T")

def tqdm(iterable: Iterable[T], *args: Any, **kwargs: Any) -> Iterator[T]: ...
def trange(start: int, end: Optional[int] = None, **kwargs: Any) -> Iterator[int]: ...
