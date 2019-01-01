import argparse
import asyncio
import logging
from collections import namedtuple
from functools import partial

logger = logging.getLogger(__name__)

Route = namedtuple("Route", ["listen_port", "destination_host", "destination_port"])

BUFFER_SIZE = 128 * 1024  # 64kb

FORMAT = "%(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)


def destination_host_display(route: Route):
    return "{}:{}".format(route.destination_host, route.destination_port)


def parse_argument(value):
    return Route(*value.split(":"))


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            writer.write(await reader.read(BUFFER_SIZE))
    finally:
        writer.close()


async def handle_client(route, local_reader, local_writer):
    try:
        logger.debug(
            "Openning connection to {}".format(destination_host_display(route))
        )
        remote_reader, remote_writer = await asyncio.open_connection(
            route.destination_host, route.destination_port
        )
        await asyncio.gather(
            pipe(local_reader, remote_writer), pipe(remote_reader, local_writer)
        )
    except (ConnectionRefusedError, OSError) as e:
        logger.warning(
            "Connection to {} refused: {}".format(destination_host_display(route), e)
        )
        pass
    finally:
        local_writer.close()


async def create_proxy_pipe(route: Route):
    server = await asyncio.start_server(
        partial(handle_client, route), "0.0.0.0", route.listen_port
    )
    logger.info(
        "Routing from {} to {}".format(
            route.listen_port, destination_host_display(route)
        )
    )
    await server.wait_closed()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-R", "--route", action="append", required=True, type=parse_argument
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    servers = [create_proxy_pipe(route) for route in args.route]
    logger.debug("Starting servers...")
    await asyncio.gather(*servers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error("Process terminated")
