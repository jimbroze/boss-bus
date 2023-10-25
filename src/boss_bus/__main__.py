"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Boss Bus."""


if __name__ == "__main__":
    main(prog_name="boss-bus")  # pragma: no cover
