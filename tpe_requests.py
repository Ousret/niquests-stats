import statistics
from concurrent.futures import ThreadPoolExecutor
from requests import Session, Response
import wassima
import time
from os import unlink

try:
    from urllib3 import ConnectionInfo

    raise RuntimeError(
        "The benchmark prerequisites aren't available. "
        "Install the legacy urllib3 prior to running this test."
    )
except ImportError:
    pass  # failsafe


def fetch(s: Session, url: str) -> list[Response]:
    sub_before = time.time()
    responses = []

    for _ in range(100):
        responses.append(s.get(url))

    print(f"subtask {time.time() - sub_before} seconds elapsed")

    return responses


if __name__ == "__main__":

    with open("./bundle.pem", "w") as fp:
        fp.write(wassima.generate_ca_bundle())

    aggregate = []

    for _ in range(60):
        before = time.time()
        tasks = []
        collect_responses = []

        with Session() as session:
            session.verify = "./bundle.pem"
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

    unlink("./bundle.pem")

    print("median", statistics.median(aggregate))
    print("average", sum(aggregate) / len(aggregate))
    print("program exit")
