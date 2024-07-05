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
            raise ValueError("Invalid media_type. Must be 'movie' or 'show'.")

        base_url = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/"
        if media_type == 'movie':
            url = f"{base_url}movie/{imdb_id}.json"
        else:
            url = f"{base_url}series/{imdb_id}:1:1.json"

        response = requests.get(url)
        data = response.json()

        releases = []
        for stream in data.get('streams', []):
            parsed_title = self._parse_title(stream['title'])
            release = {
                'title': parsed_title['title'],
                'infoHash': stream['infoHash'],
                'size_in_gb': parsed_title['size_in_gb'],
                'peers': parsed_title['peers']
            }
            releases.append(release)

        return releases

    def _parse_title(self, title: str) -> Dict[str, any]:
        """
        Parse the title string to extract size and peers information.

        Args:
            title (str): The title string containing size and peers information.

        Returns:
            Dict[str, any]: A dictionary containing the parsed information.
        """
        # Split the title into the actual title and the additional info
        parts = title.split('\n')
        actual_title = parts[0]
        
        # Initialize default values
        size_in_gb = 0
        peers = 0

        # If there's additional info, parse it
        if len(parts) > 1:
            info = parts[1]
            
            # Extract peers
            peers_match = re.search(r'👤\s*(\d+)', info)
            if peers_match:
                peers = int(peers_match.group(1))
            
            # Extract size
            size_match = re.search(r'💾\s*([\d.]+)\s*(GB|MB)', info)
            if size_match:
                size = float(size_match.group(1))
                unit = size_match.group(2)
                if unit == 'GB':
                    size_in_gb = size
                elif unit == 'MB':
                    size_in_gb = size / 1024

        return {
            'title': actual_title,
            'size_in_gb': size_in_gb,
            'peers': peers
        }
