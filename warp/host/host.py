import warnings
import traceback
import secrets
from flask import Flask, jsonify, request
from typing import Union, Callable
from types import FunctionType
from hmac import compare_digest

class Event:
    _id : int = None
    type : str = None
    def __init__(self, _type: str, **entries):
        entries["type"] = _type
        self.__dict__.update(entries)
        self._id = secrets.randbits(16)
        

class TLDServer:
    """
    Setup a TLD Server for WARP
    """
    app : Flask
    domains : dict[str, dict[str, Union[str, int]]]
    tlds : list[str]
    events : dict[str, list[FunctionType]]
    
    def __init__(self, *, app : Flask, tld : str = None, tlds : list[str] = None, domains : dict[str, dict[str, Union[str, int]]] = None):
        self.app = app
        self.domains = domains or {}
        self.tlds = tlds or [tld]
        self.tlds = [_tld.strip(".") for _tld in self.tlds]
        self.events = {}
        try:
            assert tld or tlds
        except AssertionError:
            raise ValueError("Pass either tld or tlds")
        
        def get_tld(domain_name):
            return domain_name.split(".")[-1]
        
        @app.get("/resolve/<domain_name>/")
        def resolve_domain(domain_name : str):
            domain_tld = get_tld(domain_name)
            if domain_tld not in self.tlds:
                return jsonify({"success": False, "ip": None, "reason": "Wrong server"})
            try:
                domain = self.domains[domain_name]
            except KeyError:
                return jsonify({"success": False, "ip": None, "reason": "Domain doesn't exist"})
            return jsonify({"success": True, "ip": domain["ip"], "reason": "Found"})
        
        @app.post("/set_ip/<domain_name>/")
        def set_domain_ip(domain_name : str):
            domain_tld = get_tld(domain_name)
            if domain_tld not in self.tlds:
                return jsonify({"success": False, "ip": None, "reason": "Wrong server"})
            try:
                domain = self.domains[domain_name]
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
            self.emit_event("set_domain_ip", domain_name=domain_name, ip=ip, key=key, domains=self.domains)
            return jsonify({"success": True, "ip": domain["ip"], "reason": "Updated"})
        
    def add_domain(self, domain_name = None, *, key : int, owner : str, ip : str = None):
        """
        Add a new domain. Needs its name, key and owner contact info.
        """
        self.domains[domain_name] = {"ip": ip, "key": key, "owner": owner}
        
    def on(self, event : str) -> Callable[[Callable[[Event], None]], Callable[[dict], int]]:
        """
        Add an event listener
        """
        def wrapper(func):
            if event not in self.events:
                self.events[event] = []
            self.events[event].append(func)
            def dispatcher(data : dict = None, /, **entries):
                return self.emit_event(event, **data, **entries)
            return dispatcher
        return wrapper
    
    def _emit_event(self, event : str, data : Event) -> int:
        """
        Don't use this.
        """
        amount = 0
        if not event in self.events:
            return 0
        for i in self.events[event]:
            try:
                i(data)
                amount += 1
            except Exception:
                warnings.warn(
                    f"There was an exception while trying to process an event: {traceback.format_exc()}",
                    RuntimeWarning
                )
        return amount
    
    def emit_event(self, event : Union[str, Event], **entries) -> int:
        """
        Use for emitting events. Returns how many handlers could handle the event.
        """
        data = event if isinstance(event, Event) else Event(event, **entries)
        if isinstance(event, Event):
            event = event.type
        amount = self._emit_event(event, data) + self._emit_event("any", data)
        return amount
    
