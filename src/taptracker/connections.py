import base64
import json
import os
import warnings
from pathlib import Path
from urllib.parse import urljoin

import requests

from .params import (
    BASE_URL,
    CAS_SERVER,
    CLIENT_ID,
    CLIENT_SECRET,
    KEY_FILE,
    REFRESH_TOKEN_FILE,
)

warnings.simplefilter(
    "ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def refresh_access_token():
    base64_message = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii")
    ).decode("ascii")

    payload = f"grant_type=refresh_token&refresh_token={get_refresh_token()}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {base64_message}",
    }
    url = f"{BASE_URL}/SASLogon/oauth/token#refresh_token"

    response = requests.post(url, headers=headers, data=payload, verify=False)

    os.environ["VIYA_ACCESS_TOKEN"] = json.loads(response.text)["access_token"]


def get_access_token() -> str:
    return os.environ["VIYA_ACCESS_TOKEN"]


def get_refresh_token() -> str:
    with REFRESH_TOKEN_FILE.open("r") as f:
        return f.read()


def create_cas_session():
    session_id = requests.put(
        urljoin(CAS_SERVER, "cas/sessions"),
        headers={
            "Authorization": f"Bearer {get_access_token()}",
        },
        verify=False,
    ).json()["session"]

    os.environ["VIYA_CAS_SESSION_ID"] = session_id


def get_session_id() -> str:
    return os.environ["VIYA_CAS_SESSION_ID"]


def upload_data(caslib: str, table: str, file: str | Path) -> requests.Response:
    file = Path(file)
    json_params_str = json.dumps(
        {
            "casOut": {"caslib": caslib, "name": table, "promote": "true"},
            "importOptions": {"fileType": file.suffix[1:].upper()},
        }
    )

    with file.open("rb") as f:
        data = f.read()

    return requests.put(
        urljoin(CAS_SERVER, f"cas/sessions/{get_session_id()}/actions/upload"),
        data=data,
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "binary/octet-stream",
            "JSON-Parameters": json_params_str,
        },
        verify=False,
    )


def cas_table_exists(caslib: str, table: str) -> bool:
    result = requests.post(
        urljoin(
            CAS_SERVER, f"cas/sessions/{get_session_id()}/actions/table.tableExists"
        ),
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json",
        },
        json={"caslib": caslib, "name": table},
        verify=False,
    )

    return int(result.json()["results"]["exists"])


def append_cas_table(caslib: str, base: str, data: str) -> requests.Response:
    result = requests.post(
        urljoin(
            CAS_SERVER, f"cas/sessions/{get_session_id()}/actions/dataStep.runCode"
        ),
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json",
        },
        json={"code": f"data {caslib}.{base}(append=force) ; set {caslib}.{data};run;"},
        verify=False,
    )

    return result


def delete_cas_table(caslib: str, table: str) -> requests.Response:
    result = requests.post(
        urljoin(CAS_SERVER, f"cas/sessions/{get_session_id()}/actions/table.dropTable"),
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json",
        },
        json={"caslib": caslib, "name": table},
        verify=False,
    )

    return result


def upload_key_press(
    key_press_file: str = KEY_FILE, caslib: str = "Public", table: str = "taptracker"
):
    if cas_table_exists(caslib, table):
        i = 0
        while cas_table_exists(caslib, f"{table}_i"):
            i += 1
        temp_table = f"{table}_i"
        upload_data(caslib, temp_table, key_press_file)
        append_cas_table(caslib, table, temp_table)
        delete_cas_table(caslib, temp_table)
    else:
        upload_data(caslib, table, key_press_file)


def model_get_inputs(model_id: str = "gb_predict_parkinsons"):
    url = f"{BASE_URL}/microanalyticScore/modules/{model_id}/steps"
    headers = {
        "Accept": "application/vnd.sas.collection+json",
        "Authorization": f"Bearer {get_access_token()}",
    }
    response = requests.get(url, headers=headers, verify=False).json()

    return [e["name"] for e in response["items"][-1]["inputs"]]


def model_score_presses(
    payload_dict: dict, model_id: str = "gb_predict_parkinsons"
) -> requests.Response:
    url = f"{BASE_URL}/microanalyticScore/modules/{model_id}/steps/score"
    headers = {
        "Authorization": "Bearer " + get_access_token(),
        "Content-Type": "application/vnd.sas.microanalytic.module.step.input+json",
    }

    result = requests.post(
        url, data=json.dumps(payload_dict), headers=headers, verify=False
    ).json()

    classification = result["outputs"][0]["value"]
    probability = result["outputs"][1]["value"]

    return classification, probability
