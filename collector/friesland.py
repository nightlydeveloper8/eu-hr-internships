"""Backwards-compatible Fryslân entry point; province reporting is shared."""
from .provinces import coverage, generate_province


def generate():
    return generate_province('friesland')


if __name__ == '__main__':
    print(generate()['summary'])
