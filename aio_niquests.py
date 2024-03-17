import asyncio
import statistics
import time

import niquests
from niquests import AsyncSession, Response


async def fetch(s: niquests.AsyncSession, url: str) -> list[Response]:
    sub_before = time.time()
    responses = []

    for _ in range(100):
        responses.append(await s.get(url))

    for response in responses:
        await s.gather(response)

    print(f"subtask {time.time() - sub_before} seconds elapsed")

    return responses


async def main() -> None:
    aggregate = []

    for _ in range(60):
        before = time.time()

        async with AsyncSession(multiplexed=True, pool_maxsize=10) as session:
            responses_responses = await asyncio.gather(
                *[fetch(session, "https://httpbin.local:4443/get") for _ in range(10)])
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
