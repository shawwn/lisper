from .typing import *


class SingleDispatchCallable(Generic[P, T]):
    registry: Mapping[Any, Callable[P, T]]
    def dispatch(self, cls: Any) -> Callable[P, T]: ...
    @overload
    def register(self, cls: Any) -> Callable[[Callable[P, T]], Callable[P, T]]: ...
    @overload
    def register(self, cls: Any, func: Callable[P, T]) -> Callable[P, T]: ...
    def register(self, cls: Any, func: Callable[P, T] = None): ...
    def _clear_cache(self) -> None: ...
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...

class SingleDispatchMethod(Generic[P, T]):
    dispatcher: SingleDispatchCallable[P, T]
    func: Callable[P, T]
    def __init__(self, func: Callable[P, T]) -> None: ...
    @property
    def __isabstractmethod__(self) -> bool: ...
    @overload
    def register(self, cls: type[Any], method: None = ...) -> Callable[[Callable[P, T]], Callable[P, T]]: ...
    @overload
    def register(self, cls: Callable[P, T], method: None = ...) -> Callable[P, T]: ...
    @overload
    def register(self, cls: type[Any], method: Callable[P, T]) -> Callable[P, T]: ...
    def __get__(self, obj: S, cls: Optional[Type[S]] = ...) -> Callable[P, T]: ...

