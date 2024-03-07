Performance Measurements
------------------------

Niquests is an advanced HTTP client with, on its core urllib3.future. It is capable of serving a wide
range of features, and is actually leading the field in terms of features.

In this document, we will inspect and compare the performance of Niquests against
well known clients.

### Introduction

| Client   | Constraints                                |
|----------|--------------------------------------------|
| aiohttp  | async, http/1 only, +c compiled extensions |
| httpx    | async, http/2                              |
| requests | sync only, http/1 only                     |
| niquests | async, http/2                              |

in the given matrix of client, **aiohttp** is the only one who benefit from built native C extension
to provide a nearly unchallengeable speed. The only way to fairly compare with aiohttp is by bringing
the cores of requests, httpx and niquests so that the stack/complexity execution is comparable.

we will be as fair as possible across all clients by providing the closest alike execution.

### Established Scenario

The shared pool connection MUST not exceed 10 connections. The internals are free to scale at will in given limits.

Spawn 10 tasks, each task share the same "pool" of connection, and each task fetch 100 responses.
The responses are collected through the main task. Each sub-task have a time counter along with the main one.

We include, in spent time, the construction of the ssl context with the system CAs.
The response count must be exactly 1000, and each response must have its (bytes) content loaded.

Each script must run exactly 60 times, and data must be aggregated afterward. The average delays are kept.
A reasonable delay of 60 seconds must be respected between each script to avoid penalizing the performance
due to CPU throttling.

We must ensure that we eliminate:

- Network latency by either running the server locally or in a home network (wired).
- It's recommended that, you must have at least 8c/16t available on the server/client side(s). 
- Constrain the TLS version and cipher to ensure OpenSSL alignments with all clients.

The delay must be computed after contextmanager exit (aka. pool shutdown).
Of course, don't do anything else during the benchmarks, nothing.

### Prerequisites

Tools you must have in your environment:

- mkcert
- docker
- compose plugin v2

The server will be handled by both:

- Traefik
- gohttpbin (x6 replicas)

### Main execution script

```shell
$ mkcert httpbin.local -cert-file ./certs/httpbin.local.pem -key-file ./certs/httpbin.local.key
$ echo "127.0.0.1   httpbin.local" | sudo tee -a /etc/hosts
$ docker compose up -d
$ pip install -r requirements.txt
$ python aio_httpx.py
$ python aio_niquests.py
$ python tpe_requests.py
$ python aio_httpx_core.py
$ python aio_niquests_core.py
$ python tpe_requests_core.py
$ python aio_aiohttp.py
```

### Results

The scenario is executed on a mid-range laptop, running Fedora 38 with Python 3.11.
CPU: 12th Gen Intel® Core™ i7, 32 GiB of DDR4.

High-level APIs

| Client   | Average Delay to Complete |
|----------|---------------------------|
| requests | 987 ms                    |
| httpx    | 735 ms                    |
| niquests | 600 ms                    |

---

Simplified APIs

| Client        | Average Delay to Complete |
|---------------|---------------------------|
| requests core | 643 ms                    |
| httpx core    | 550 ms                    |
| aiohttp       | 220 ms                    |
| niquests core | 210 ms                    |

Niquests is not going to settle with these numbers, we're constantly thinking of innovative ways
to speed things up. Nevertheless, it performs the best overall, with this level of features and being native Python.

The actual delays heavily depends on your CPU capabilities and your interpreter version. 
The factors should remain the same.
