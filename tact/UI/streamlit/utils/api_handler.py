from typing import Any, Dict, Optional, Union
import requests


class ApiHandler:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_settings(
        self, config_type: str, field: Optional[str] = None
    ) -> Union[Dict, Any]:
        url = f"{self.base_url}/config/{config_type}"
        params = {"field": field} if field else {}
        response = requests.get(url, params=params)

        if response.ok:
            if field:
                return response.text.replace('"', "")
            else:
                return response.json
        else:
            raise Exception(
                f"Failed to get settings for {config_type}: {response.status_code}"
            )

    def update_settings(self, config_type: str, settings_dict: Dict):
        url = f"{self.base_url}/config/{config_type}"
        response = requests.patch(url, json={"outgoing_config_json": settings_dict})
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

    def generate_preview(self):
        url = f"{self.base_url}/preview"
        response = requests.get(url)
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
