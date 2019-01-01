import asyncio

import uvloop

uvloop.install()

BUFFER_SIZE = 4096


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            writer.write(await reader.read(BUFFER_SIZE))
    finally:
        writer.close()


async def create_proxy_pipe(listen_port, destination_host, destination_port):
    async def handle_client(local_reader, local_writer):
        try:
            remote_reader, remote_writer = await asyncio.open_connection(
                destination_host, destination_port
            )
            pipe1 = pipe(local_reader, remote_writer)
            pipe2 = pipe(remote_reader, local_writer)
            await asyncio.gather(pipe1, pipe2)
        finally:
            local_writer.close()

    server = await asyncio.start_server(handle_client, "0.0.0.0", listen_port)
    print("Serving on {}".format(server.sockets[0].getsockname()))
    await server.wait_closed()


async def main():
    await asyncio.gather(create_proxy_pipe(8888, "127.0.0.1", 8889))


if __name__ == "__main__":
    asyncio.run(main())
