"""
For resolving domains
"""
import requests
from .servers import SERVERS

def resolve(domain : str) -> list[tuple[str, int]]:
    domain = domain.removesuffix("<warp>").split(".")
    tld = domain.pop(-1)
    try:
        server = SERVERS[tld]
    except KeyError:
        raise ValueError("No such TLD.")
    try:
        resp = requests.get(f"https://{server}/resolve/{'.'.join(domain)}.{tld}/", timeout=5).json()
    except TimeoutError:
        raise TimeoutError("Server could not be reached.")
    try:
        assert resp.get("SUCCESS")
    except AssertionError:
        reason = resp.get("REASON")
        if reason == "Domain doesn't exist":
            raise NameError("Domain does not exist")
        raise ConnectionError(f"There was an error while getting the ip: {reason}")
    return resp["IP"]