from flask import Flask, jsonify, request
from typing import Union
from hmac import compare_digest

def host_tld_server(*, app : Flask, tld : str, domains : dict[str, dict[str, Union[str, int]]]) -> Flask:
    @app.get("/resolve/<domain_name>/")
    def resolve_domain(domain_name : str):
        if not domain_name.endswith("."+tld):
            return jsonify({"success": False, "ip": None, "reason": "Wrong server"})
        try:
            domain = domains[domain_name]
        except KeyError:
            return jsonify({"success": False, "ip": None, "reason": "Domain doesn't exist"})
        return jsonify({"success": True, "ip": domain["ip"], "reason": "Found"})
    
    @app.post("/set_ip/<domain_name>/")
    def set_domain_ip(domain_name : str):
        if not domain_name.endswith("."+tld):
            return jsonify({"success": False, "ip": None, "reason": "Wrong server"})
        try:
            domain = domains[domain_name]
        except KeyError:
            return jsonify({"success": False, "ip": None, "reason": "Domain doesn't exist"})
        data = request.json
        key = data["key"]
        ip = data["ip"]
        try:
            assert compare_digest(key, domain["key"])
        except AssertionError:
            return jsonify({"success": False, "ip": None, "reason": "Failed Authentication"})
        try:
            assert isinstance(ip, str)
        except AssertionError:
            return jsonify({"success": False, "ip": None, "reason": "IP needs to be a string"})
        domain["ip"] = ip
        return jsonify({"success": True, "ip": domain["ip"], "reason": "Updated"})
    return app