import asyncio
import time
import aiohttp
import wassima
import statistics


async def fetch(c: aiohttp.ClientSession, url: str) -> list[aiohttp.ClientResponse]:
    sub_before = time.time()
    responses = []

    for _ in range(100):
        responses.append(await c.get(url))

    print(f"subtask {time.time() - sub_before} seconds elapsed")

    return responses


async def main() -> None:
    aggregate = []

    for _ in range(60):
        before = time.time()

        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=10, ssl=wassima.create_default_ssl_context()), ) as s:
            responses_responses = await asyncio.gather(
                *[fetch(s, "https://httpbin.local:4443/get") for _ in range(10)])

            responses = [item for sublist in responses_responses for item in sublist]

        delay = time.time() - before

        print(f"main task {delay} seconds elapsed for {len(responses)} response(s)")
        aggregate.append(delay)

        await asyncio.sleep(1)

    print("median", statistics.median(aggregate))
    print("average", statistics.mean(aggregate))

    print("program exit")


if __name__ == "__main__":
    asyncio.run(main())
