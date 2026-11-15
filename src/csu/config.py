"""Configuration model. Secrets are never stored here.

``storage_options`` builds delta-rs credential options from the selected
identity mode, reading any secret value from the process environment at runtime.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class EnvironmentConfig:
    environment_id: str
    dataverse_url: str


@dataclass
class Config:
    tenant_id: str = "<tenant-id>"
    client_id: str = "<client-id>"
    identity_mode: str = "managed_identity"  # managed_identity | service_principal | azure_cli
    delta_base_uri: str = ".local/delta"
    storage_account: str = "<storage-account>"
    storage_container: str = "usage"
    landing_container: str = "landing"
    page_size: int = 5000
    enable_user_level_credit_api: bool = False
    environments: List[EnvironmentConfig] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        import yaml  # lazy; only needed when loading a YAML file
        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        envs = [EnvironmentConfig(**e) for e in raw.pop("environments", [])]
        return cls(environments=envs, **raw)

    def storage_options(self) -> Dict[str, str]:
        """delta-rs object_store options. No account keys are ever returned."""
        opts: Dict[str, str] = {"account_name": self.storage_account}
        mode = self.identity_mode
        if mode == "managed_identity":
            opts["use_azure_cli"] = "false"
            msi = os.environ.get("IDENTITY_ENDPOINT") or os.environ.get("MSI_ENDPOINT")
            if msi:
                opts["msi_endpoint"] = msi
        elif mode == "service_principal":
            opts["client_id"] = self.client_id
            opts["tenant_id"] = self.tenant_id
            secret = os.environ.get("AZURE_CLIENT_SECRET")
            if secret:
                opts["client_secret"] = secret
        elif mode == "azure_cli":
            opts["use_azure_cli"] = "true"
        return opts
