import argparse
import asyncio
from collections import namedtuple
from functools import partial

Route = namedtuple("Route", ["listen_port", "destination_host", "destination_port"])

BUFFER_SIZE = 4096


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
        remote_reader, remote_writer = await asyncio.open_connection(
            route.destination_host, route.destination_port
        )
        await asyncio.gather(
            pipe(local_reader, remote_writer), pipe(remote_reader, local_writer)
        )
    except ConnectionRefusedError:
        print("Connection to {} refused".format(destination_host_display(route)))
        pass
    finally:
        local_writer.close()


async def create_proxy_pipe(route: Route):
    server = await asyncio.start_server(
        partial(handle_client, route), "0.0.0.0", route.listen_port
    )
    print(
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
    args = parser.parse_args()
    servers = [create_proxy_pipe(route) for route in args.route]
    print("Starting servers...")
    await asyncio.gather(*servers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Process terminated")
