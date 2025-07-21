"""
CMD implements the command-line interface (CLI) for multiport.
"""
import logging
from typing import Tuple

import click
import tqdm

from .scanner import Scanner


@click.command()
@click.option("-H", "--host", required=True, type=str, help="The target host.")
@click.option(
    "-p",
    "--ports",
    type=click.IntRange(1, 65536),
    multiple=True,
    help="The target port, supports multiple usage.",
)
@click.option(
    "-m",
    "--min-port",
    type=click.IntRange(1, 65536),
    help="The lowest port to be scanned.",
)
@click.option(
    "-M",
    "--max-port",
    type=click.IntRange(1, 65536),
    help="The highest port to be scanned.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
def multiport(
    host: str, ports: Tuple[int], min_port: int, max_port: int, verbose: bool
):
    """
    multiport is a port scanner that searches for open ports on a given host.

    If --ports is set, all given ports will be scanned.

    If --min-port or --max-port are set, all ports in the interval will be
    scanned (--min-port defaults to 0 and --max-port defaults to 65536 if only
    one is set).

    \b
    Examples:
        $ multiport --host localhost --port 80 --port 443
        $ multiport --host localhost --min-port 80 --max-port 443
        $ multiport --host localhost --min port 80
        $ multiport --host localhost --max-port 443

    """
    if not any([ports, min_port, max_port]):
        msg = "One of --port, --min-port, or --max-port must be set."
        raise click.UsageError(msg)

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    scanner = Scanner(host=host)

    if ports:
        for port in tqdm.tqdm(ports):
            scanner.scan(port=port)
    else:
        min_port = min_port or 0
        max_port = max_port or 65536

        for port in tqdm.trange(min_port, max_port):
            scanner.scan(port=port)

    if not scanner.open_ports:
        click.echo(f"No open ports on host {scanner.host} found.")
    else:
        click.echo(f"The following ports are open on host {scanner.host}:")
        for port in scanner.open_ports:
            click.echo(f"\t- Port {port}")
