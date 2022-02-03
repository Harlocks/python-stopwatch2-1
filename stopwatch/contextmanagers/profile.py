import atexit
import functools
import math
from typing import Any, Callable, TypeVar

from termcolor import colored

from ..statistics import Statistics
from ..stopwatch import Stopwatch
from . import Caller, format_elapsed_time, inspect_caller

RT = TypeVar('RT')  # return type


def make_report(caller: Caller, name: str, statistics: Statistics) -> str:
    tag = ''.join([
        colored(f'[{caller.module}', color='blue', attrs=['bold']),
        colored(f'#{name}', color='green', attrs=['bold']),
        colored(']', color='blue', attrs=['bold'])
    ])
    items = ', '.join([
        f'hits={len(statistics)}',
        f'mean={format_elapsed_time(statistics.mean)}',
        f'min={format_elapsed_time(statistics.minimum)}',
        f'median={format_elapsed_time(statistics.median)}',
        f'max={format_elapsed_time(statistics.maximum)}',
        f'dev={format_elapsed_time(math.sqrt(statistics.variance))}'
    ])

    return f'{tag} {items}'


def print_report(caller: Caller, name: str, statistics: Statistics) -> None:
    if len(statistics) > 0:
        print(make_report(caller, name, statistics))


def profile(**kwargs: Any) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    caller = inspect_caller()

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        name: str = kwargs.get('name', func.__name__)
        report_every: int = kwargs.get('report_every', 1)
        should_report = report_every is not None

        statistics = Statistics()
        atexit.register(print_report, caller, name, statistics)

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> RT:
            with Stopwatch() as stopwatch:
                result = func(*args, **kwargs)

            statistics.add(stopwatch.elapsed)
            if should_report and (len(statistics) % report_every) == 0:
                print_report(caller, name, statistics)

            return result

        return wrapper

    return decorator
