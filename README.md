# Beginner.Codes Python Package

This is the official Python Package for the Beginner.Codes Discord server.

## Running Challenge Tests

- Install the package: `pip install beginner.codes`
- Import the test runner: `from beginnercodes.challenges import test`
- Run the tests, passing in the challenge number and your solution function: `test(458, n_differences)`
- Optionally, you can add two options `description=True` and `examples=True` to print out the challenge information without leaving the terminal
```python
from beginnercodes.challenges import test

def n_differences(nums: list[int]) -> int:
    return 0  # Your code goes here!!!


test(458, n_differences)
test(458, n_differences, description=True)
test(458, n_differences, examples=True)
test(458, n_differences, True, True) # for both
```
This will handle downloading the necessary challenge test cases and will run them against your code. It will show you which tests failed, what went wrong, and how many tests succeeded.

