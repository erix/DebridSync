import requests
from typing import List, Dict, Literal
from .release_finder import ReleaseFinder
import re

class Torrentio(ReleaseFinder):
    def find_releases(self, imdb_id: str, media_type: Literal['movie', 'show']) -> List[Dict[str, str]]:
        """
        Find releases for a given IMDb ID and media type using Torrentio.

        Args:
            imdb_id (str): The IMDb ID of the movie or TV show.
            media_type (Literal['movie', 'show']): The type of media, either 'movie' or 'show'.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing release information.

        Raises:
            ValueError: If an invalid media_type is provided.
        """
        if media_type not in ['movie', 'show']:
            raise ValueError("Invalid media_type. Must be either 'movie' or 'show'.")

        url = f"https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/{media_type}/{imdb_id}.json"
        response = requests.get(url)
        data = response.json()

        releases = []
        for stream in data.get('streams', []):
            parsed_info = self._parse_title(stream['title'])
            release = {
                'title': parsed_info['title'],
                'infoHash': stream['infoHash'],
                'size_in_gb': parsed_info['size_in_gb'],
                'peers': parsed_info['peers']
            }
            releases.append(release)

        return releases

    def _parse_title(self, title: str) -> Dict[str, any]:
        """
        Parse the title string to extract additional information.

        Args:
            title (str): The title string containing additional information.

        Returns:
            Dict[str, any]: A dictionary containing parsed information.
        """
        # Split the title into main title and additional info
        parts = title.split('\n')
        main_title = parts[0]
        
        # Initialize default values
        size_in_gb = 0
        peers = 0

        # Parse additional info if available
        if len(parts) > 1:
            info = parts[1]
            size_match = re.search(r'💾\s*([\d.]+)\s*(GB|MB)', info)
            if size_match:
                size = float(size_match.group(1))
                unit = size_match.group(2)
                size_in_gb = size if unit == 'GB' else size / 1024

            peers_match = re.search(r'👤\s*(\d+)', info)
            if peers_match:
                peers = int(peers_match.group(1))

        return {
            'title': main_title,
            'size_in_gb': round(size_in_gb, 2),
            'peers': peers
        }
