from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional
from requests import Response
from rich.markdown import Markdown
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich import box
import requests


class ChallengeNotFound(Exception):
    ...


class StatusEnum(Enum):
    SUCCESS = auto()
    FAILED = auto()
    EXCEPTION = auto()


@dataclass()
class Result:
    index: int
    expected: Any
    got: Any = field(default=None)
    status: StatusEnum = field(default=StatusEnum.SUCCESS)


USAGE = """# **USAGE** 
```py
test(challenge: int, your_function: func, description: bool, examples: bool) 
---
test(458, your_function)   # runs all tests cases on your function  
test(458, your_function, description=True)  # adds the test description in the terminal
test(458, your_function, examples=True)  # adds test examples in the terminal
test(458, your_function, True, True)  # adds both description and examples
test(458, description=True)  # prints only description without running tests
test(458, examples=True)  # same as above but with examples
``` 
"""


def build_table():
    _t = Table(title='[bold]Test Results[/bold]', highlight=True, box=box.MINIMAL)
    _t.add_column("#:", justify='right')
    _t.add_column("Expected:", justify='center')
    _t.add_column("Got:")
    return _t


def test(challenge: int, solution_func: Optional = None, description: bool = False, examples: bool = False):
    console = Console(theme=Theme({'numbers': 'blue', 'expected': 'green', 'got': 'red', 'final': 'yellow'}))

    # These functions must be protected to ensure no CHEATING happens. #
    def _fetch_data(url: str) -> Response:
        _r = requests.get(url)
        if _r.status_code == 404:
            raise ChallengeNotFound(f"Challenge {challenge} is not found")
        return _r

    def _get_tests(challenge: int) -> list[dict]:
        url = f"https://raw.githubusercontent.com/beginner-codes/challenges/main/weekday/test_cases_{challenge}.json"
        response = _fetch_data(url)
        return response.json()

    def _get_info(challenge: int, description: bool, examples: bool) -> str:
        url = f"https://raw.githubusercontent.com/beginner-codes/challenges/main/weekday/challenge_{challenge}.md"
        result = ''
        if description or examples:
            info = _fetch_data(url)
            try:
                if description:
                    result += info.text.split('##')[0]
                if examples:
                    result += '# ' + info.text.split('# ')[2].replace('#', '')

            except IndexError as e:
                result += e
        return result + '***'

    def _run_tests(tests: list[dict], solution_func) -> list[Result]:
        results = []
        for index, test_case in enumerate(tests, start=1):
            result = Result(index, test_case["return"])
            try:
                result.got = solution_func(*test_case["args"])
            except Exception as exp:
                result.status = StatusEnum.EXCEPTION
                result.got = exp
            else:
                if result.got != test_case["return"]:
                    result.status = StatusEnum.FAILED

            results.append(result)

        return results

    def _show_results(challenge: int, results: list[Result], total_tests: int, info: str):
        failures = 0
        console.print(Markdown(info))
        results_table = build_table()

        for result in results:
            if result.status == StatusEnum.FAILED:
                results_table.add_row(
                    f"[numbers]{result.index}[/numbers]",
                    f"[expected]{result.expected}[/expected]",
                    f"[got]{result.got}[/got]"
                )
                failures += 1

            elif result.status == StatusEnum.EXCEPTION:
                results_table.add_row(
                    f"Test {result.index} failed",
                    "",
                    f"{result.got!r}")
                failures += 1

        if failures:
            console.print(results_table)

        if total_tests:
            console.print(f"---- Challenge {challenge} Results ----", style='final')
            console.print(f"[expected]{total_tests - failures}[/expected] passed, [got]{failures}[/got] failed")

            if not failures:
                console.print("\n[expected][bold]**** Great job!!! ****")

    if solution_func:
        tests = _get_tests(challenge)
        results = _run_tests(tests, solution_func)
    else:
        tests = []
        results = []
    if any([solution_func, examples, description]):
        info = _get_info(challenge, description, examples)
    else:
        info = USAGE

    _show_results(challenge, results, len(tests), info)
