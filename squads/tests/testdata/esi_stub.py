import json
from pathlib import Path

from app_utils.esi_testing import EsiClientStub, EsiEndpoint


def load_test_data():
    file_path = Path(__file__).parent / "esi.json"
    with file_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


_esi_data = load_test_data()

_endpoints = []

esi_client_stub = EsiClientStub(_esi_data, endpoints=_endpoints)
esi_client_error_stub = EsiClientStub(_esi_data, endpoints=_endpoints, http_error=True)
