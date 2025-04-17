import argparse
import trio


def parse_args():
    parser = argparse.ArgumentParser(description="Process two files.")

    # Add the first file argument
    parser.add_argument("input", type=str,
                        help="The path to the first file.")

    # Add the second file or directory argument
    parser.add_argument("file2_or_dir", type=str,
                        help="The path to either a single file or a directory containing files. We do not recurse.")

    parser.add_argument("--size", type=int,
                        help="We only try to find the first --size bytes")

    parser.add_argument("--offset", type=int, default=0,
                        help="We skip the first --offset bytes")

    args = parser.parse_args()
    return args

    # Process the files/directory here


async def read_file(path):
    base_path = trio.Path(path)
    if await base_path.is_file():
        return await base_path.read_bytes()


async def read_dir_or_file(path: str, queue: trio.MemorySendChannel):
    base_path = trio.Path(path)
    if await base_path.is_file():
        await queue.send(await base_path.read_bytes())
    else:
        for item in await base_path.iterdir():
            if await item.is_file():
                await queue.send((item, await item.read_bytes()))
    await queue.aclose()


async def compare(base_file_t, is_in_file_t, size=None, offset=0):
    base_file_name, base_file = base_file_t
    is_in_file_name, is_in_file = is_in_file_t
    if len(is_in_file) < offset:
        return
    if size is not None:
        index = base_file.find(is_in_file[offset:size+offset])
    else:
        index = base_file.find(is_in_file[offset:])
    if index != -1:
        print(f"{is_in_file_name} is in {base_file_name} at offset {index}")
    else:
        pass
        # print(f"{is_in_file_name} is not in {base_file_name}")


async def _main():
    args = parse_args()
    send_queue, recv_queue = trio.open_memory_channel(1)
    f_file = await read_file(args.input)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(read_dir_or_file, args.file2_or_dir, send_queue)
        while True:
            try:
                x = await recv_queue.receive()
                # print(f"recved {x[0]} as {len(x[1])} bytes")
            except trio.EndOfChannel:
                break
            await compare((args.input, f_file), x, size=args.size, offset=args.offset)


def main():
    trio.run(_main)


if __name__ == "__main__":
    main()
