"""
Set an ip of a domain
"""
import requests
from .servers import SERVERS

def set_ip(*, domain_name, ip, key):
    domain = domain_name
    domain = domain.removesuffix("<warp>").split(".")
    tld = domain.pop(-1)
    try:
        server = SERVERS[tld]
    except KeyError:
        raise ValueError("No such TLD.")
    try:
        resp = requests.post(f"https://{server}/set_ip/{'.'.join(domain)}.{tld}/", timeout=5, json={"key": key, "ip": ip}).json()
    except TimeoutError:
        raise TimeoutError("Server could not be reached.")
    try:
        assert resp.get("SUCCESS")
    except AssertionError:
        reason = resp.get("REASON")
        if reason == "Domain doesn't exist":
            raise NameError("Domain does not exist")
        if reason == "Failed Authentication":
            raise PermissionError("Failed Authentication")
        raise ConnectionError(f"There was an error while getting the ip: {reason}")
    return resp["ip"]
