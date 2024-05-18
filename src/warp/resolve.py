"""
For resolving domains
"""
import requests

SERVERS = {}

def resolve(domain : str) -> list[tuple[str, int]]:
    domain = domain.removesuffix("<warp>").split(".")
    tld = domain.pop(-1)
    try:
        server = SERVERS[tld]
    except KeyError:
        raise ValueError("No such TLD.")
    try:
        resp = requests.get(f"https://{server}/resolve/{".".join(domain)}.{tld}", timeout=5).json()
    except TimeoutError:
        raise TimeoutError("Server could not be reached.")
    try:
        assert resp["SUCCESS"]
    except AssertionError:
        raise ConnectionError("There was an error while getting the ip.")
    return resp["IP"]