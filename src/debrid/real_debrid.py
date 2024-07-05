import requests
from typing import Dict, Any

class RealDebrid:
    BASE_URL = "https://api.real-debrid.com/rest/1.0"

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def add_torrent(self, torrent_hash: str) -> Dict[str, Any]:
        """
        Add a torrent to Real-Debrid using its hash.

        Args:
            torrent_hash (str): The hash of the torrent to add.

        Returns:
            Dict[str, Any]: The response from the Real-Debrid API.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        url = f"{self.BASE_URL}/torrents/addMagnet"
        data = {
            "magnet": f"magnet:?xt=urn:btih:{torrent_hash}",
        }

        response = requests.post(url, headers=self.headers, data=data)
        response.raise_for_status()
        return response.json()

    def select_files(self, torrent_id: str, file_ids: str = "all") -> None:
        """
        Select files to download from the added torrent.

        Args:
            torrent_id (str): The ID of the torrent returned by add_torrent.
            file_ids (str): Comma-separated file IDs or "all" to select all files.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        url = f"{self.BASE_URL}/torrents/selectFiles/{torrent_id}"
        data = {
            "files": file_ids,
        }

        response = requests.post(url, headers=self.headers, data=data)
        response.raise_for_status()

    def get_torrent_info(self, torrent_id: str) -> Dict[str, Any]:
        """
        Get information about a specific torrent.

        Args:
            torrent_id (str): The ID of the torrent.

        Returns:
            Dict[str, Any]: The torrent information.

        Raises:
            requests.RequestException: If there's an error with the API request.
        """
        url = f"{self.BASE_URL}/torrents/info/{torrent_id}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
