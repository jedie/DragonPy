"""
    Allow dragonpy to be executable
    through `python -m dragonpy`.
"""


from dragonpy.cli import cli_app


def main():
    cli_app.main()


if __name__ == '__main__':
    main()
