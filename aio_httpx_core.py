import asyncio
import statistics
import time
import wassima
from httpcore import AsyncConnectionPool, Response


async def fetch(s: AsyncConnectionPool, url: str) -> list[Response]:
    sub_before = time.time()
    responses = []

    for _ in range(100):
        responses.append(await s.request("GET", url))

    print(f"subtask {time.time() - sub_before} seconds elapsed")

    return responses


async def main() -> None:
    aggregate = []

    for _ in range(60):
        before = time.time()
        async with AsyncConnectionPool(http2=True, ssl_context=wassima.create_default_ssl_context(),
                                       max_connections=10) as s:
            responses_responses = await asyncio.gather(
                *[fetch(s, "https://httpbin.local:4443/get") for _ in range(10)])
            responses = [item for sublist in responses_responses for item in sublist]

        delay = time.time() - before
        print(f"main task {delay} seconds elapsed with {len(responses)} response(s)")
        aggregate.append(delay)
        await asyncio.sleep(1)

    print("median", statistics.median(aggregate))
    print("average", sum(aggregate) / len(aggregate))
    print("program exit")


if __name__ == "__main__":
    asyncio.run(main())
