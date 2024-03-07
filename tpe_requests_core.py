import statistics
from concurrent.futures import ThreadPoolExecutor
from urllib3 import PoolManager, BaseHTTPResponse
import wassima
import time

try:
    from urllib3 import ConnectionInfo

    raise RuntimeError(
        "The benchmark prerequisites aren't available. "
        "Install the legacy urllib3 prior to running this test."
    )
except ImportError:
    pass  # failsafe


def fetch(s: PoolManager, url: str) -> list[BaseHTTPResponse]:
    sub_before = time.time()
    responses = []

    for _ in range(100):
        responses.append(s.urlopen("GET", url))

    print(f"subtask {time.time() - sub_before} seconds elapsed")

    return responses


if __name__ == "__main__":

    aggregate = []

    for _ in range(60):
        before = time.time()
        tasks = []
        collect_responses = []

        with PoolManager(ca_cert_data=wassima.generate_ca_bundle()) as session:
            with ThreadPoolExecutor(max_workers=10) as tpe:
                for _ in range(10):
                    tasks.append(
                        tpe.submit(fetch, session, "https://httpbin.local:4443/get")
                    )

                for task in tasks:
                    collect_responses.extend(task.result())

        delay = time.time() - before

        print(f"main task {delay} seconds elapsed with {len(collect_responses)} response(s)")
        aggregate.append(delay)
        time.sleep(1)

    print("median", statistics.median(aggregate))
    print("average", statistics.mean(aggregate))
    print("program exit")
