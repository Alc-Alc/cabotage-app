from __future__ import annotations

import os
from typing import TYPE_CHECKING

import consul

from cabotage.utils.context import modified_environ
from flask import g

if TYPE_CHECKING:
    from cabotage._types.server import TypedFlask


class Consul(object):
    def __init__(self, app: TypedFlask | None = None) -> None:
        self.app = app
        self.consul_host = "127.0.0.1"
        self.consul_port = 8500
        self.consul_scheme = "http"
        self.consul_verify = False
        self.consul_cert: str | tuple[str, str] | None = None
        self.consul_prefix = "cabotage"
        self.consul_token_file = os.path.expanduser("~/.consul-token")
        self.consul_token: str | None = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: TypedFlask) -> None:
        self.consul_host = app.config.get("CONSUL_HOST", self.consul_host)
        self.consul_port = app.config.get("CONSUL_PORT", self.consul_port)
        self.consul_scheme = app.config.get("CONSUL_SCHEME", self.consul_scheme)
        self.consul_verify = app.config.get("CONSUL_VERIFY", self.consul_verify)
        self.consul_cert = app.config.get("CONSUL_CERT", self.consul_cert)
        self.consul_prefix = app.config.get("CONSUL_PREFIX", self.consul_prefix)
        self.consul_token_file = app.config.get(
            "CONSUL_TOKEN_FILE", self.consul_token_file
        )
        self.consul_token = app.config.get("CONSUL_TOKEN", self.consul_token)

        if self.consul_token is None:
            if os.path.exists(self.consul_token_file):
                with open(self.consul_token_file, "r") as consul_token_file:
                    self.consul_token = consul_token_file.read().lstrip().rstrip()

        app.teardown_appcontext(self.teardown)

    def connect_consul(self) -> consul.Consul:
        # Ignore default environment variables
        with modified_environ(
            "CONSUL_HTTP_ADDR", "CONSUL_HTTP_SSL", "CONSUL_HTTP_SSL_VERIFY"
        ):
            consul_client = consul.Consul(
                host=self.consul_host,
                port=self.consul_port,
                scheme=self.consul_scheme,
                verify=self.consul_verify,
                cert=self.consul_cert,
                token=self.consul_token,
            )
        return consul_client

    def teardown(self, exception: BaseException | None) -> None:
        g.pop("consul_client", None)

    @property
    def consul_connection(self) -> consul.Consul:
        if "consul_client" not in g:
            g.consul_client = self.connect_consul()
        return g.consul_client
