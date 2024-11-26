from typing import Any, Dict, Optional, Union
import requests


class ApiHandler:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_config(
        self, config_type: str, field: Optional[str] = None
    ) -> Union[Dict, Any]:
        url = f"{self.base_url}/config/{config_type}"
        params = {"field": field} if field else {}
        response = requests.get(url, params=params)

        if response.ok:
            if field:
                return response.text.replace('"', "")
            else:
                return response.json()
        else:
            raise Exception(
                f"Failed to get settings for {config_type}: {response.status_code}"
            )

    def get_data(self, format: Optional[str] = None, nrows: Optional[int] = None, request_type: Optional[str] = None):
        url = f"{self.base_url}/data"
        params = {}

        if format:
            params["format"] = format
        if nrows:
            params["nrows"] = nrows
        if request_type:
            params["request_type"] = request_type

        response = requests.get(url, params=params)

        if response.ok:
            full_response = response.json()
            return full_response.get("data")
        else:
            raise Exception(f"Failed to get data: {response.status_code}")

    def update_config(self, config_type: str, config_to_apply: Dict):
        url = f"{self.base_url}/config/{config_type}"
        response = requests.patch(url, json=config_to_apply)
        if response.status_code == 200:
            return True
        else:
            raise Exception(
                f"Failed to update settings for {config_type}: {response.status_code}"
            )

    def analyze(self):
        url = f"{self.base_url}/analysis"
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            raise Exception(f"Failed to analyze: {response.status_code}")

    def generate_preview(self, preview_type: str = None):
        params = {"preview_type": preview_type}

        url = f"{self.base_url}/preview"
        response = requests.get(url, params=params) if params else requests.get(url)

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"Failed to generate preview: {response.status_code}")

    def process(self):
        url = f"{self.base_url}/process"
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            raise Exception(f"Failed to process: {response.status_code}")

    def transform(self, operation: str):
        params = {"operation": operation}

        url = f"{self.base_url}/transform"
        response = requests.post(url, params=params)
        if response.ok:
            return True
        else:
            raise Exception(f"Failed to transform dataset: {response.status_code}")
