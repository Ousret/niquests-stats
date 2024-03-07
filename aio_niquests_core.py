import asyncio
import statistics
import time

from urllib3_future import AsyncPoolManager, AsyncHTTPResponse
import wassima


async def fetch(pool: AsyncPoolManager, url: str) -> list[AsyncHTTPResponse]:
    before = time.time()
    promises = []
    responses = []

    for _ in range(100):
        promises.append(await pool.urlopen("GET", url, multiplexed=True))

    for promise in promises:
        responses.append(await pool.get_response(promise=promise))

    print(f"subtask {time.time() - before} seconds elapsed")

    return responses


async def main() -> None:
    aggregate = []

    for _ in range(60):
        before = time.time()
        async with AsyncPoolManager(maxsize=10, ca_cert_data=wassima.generate_ca_bundle()) as s:
            responses_responses = await asyncio.gather(
                *[fetch(s, "https://httpbin.local:4443/get") for _ in range(10)])
            responses = [item for sublist in responses_responses for item in sublist]

        delay = time.time() - before
        print(f"main task {delay} seconds elapsed with {len(responses)} response(s)")
        aggregate.append(delay)

        await asyncio.sleep(1)

    print("median", statistics.median(aggregate))
    print("average", statistics.mean(aggregate))
    print("program exit")


if __name__ == "__main__":
    asyncio.run(main())
