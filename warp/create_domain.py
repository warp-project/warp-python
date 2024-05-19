"""
Create a new domain
"""
from typing import Union
import requests
from .servers import SERVERS

def create_domain(*, domain_name : str, key : str, owner : str) -> Union[str, int]:
    """
    Create a new domain
    """
    domain = domain_name
    domain = domain.removesuffix("<warp>").split(".")
    tld = domain.pop(-1)
    try:
        server = SERVERS[tld]
    except KeyError:
        raise ValueError("No such TLD.")
    try:
        resp = requests.post(f"https://{server}/new_domain/{'.'.join(domain)}.{tld}/", timeout=5, json={"access_key": key, "owner": owner}).json()
    except TimeoutError:
        raise TimeoutError("Server could not be reached.")
    try:
        assert resp.get("success")
    except AssertionError:
        reason = resp.get("reason")
        if reason == "Unauthorized":
            raise PermissionError("Failed Authentication")
        raise Exception(f"There was an error while creating the domain: {reason}")
    return resp["key"]
