import requests
from typing import List, Literal, Dict, Any
import re
from .release_finder import ReleaseFinder
from models.release import Release

class Torrentio(ReleaseFinder):
    def find_releases(self, imdb_id: str, media_type: Literal['movie', 'show', 'episode']) -> List[Release]:
        """
        Find releases for a given IMDb ID and media type using Torrentio.

        Args:
            imdb_id (str): The IMDb ID of the movie, TV show, or episode.
            media_type (Literal['movie', 'show', 'episode']): The type of media, either 'movie', 'show', or 'episode'.

        Returns:
            List[Release]: A list of Release objects containing release information.

        Raises:
            ValueError: If an invalid media_type is provided.
        """
        if media_type not in ['movie', 'show', 'episode']:
            raise ValueError("Invalid media_type. Must be 'movie', 'show', or 'episode'.")

        base_url = "https://torrentio.strem.fun/sort=qualitysize|qualityfilter=480p,scr,cam/stream/"
        
        if media_type == 'movie':
            url = f"{base_url}movie/{imdb_id}.json"
        elif media_type == 'show':
            url = f"{base_url}series/{imdb_id}:1:1.json"
        else:  # episode
            url = f"{base_url}series/{imdb_id}.json"

        response = requests.get(url)
        data = response.json()

        releases = []
        for stream in data.get('streams', []):
            parsed_title = self._parse_title(stream['title'])
            release = Release(
                title=parsed_title['title'],
                infoHash=stream['infoHash'],
                size_in_gb=parsed_title['size_in_gb'],
                peers=parsed_title['peers']
            )
            releases.append(release)

        return releases

    def _parse_title(self, title: str) -> Dict[str, Any]:
        """
        Parse the title string to extract size and peers information.

        Args:
            title (str): The title string containing size and peers information.

        Returns:
            Dict[str, any]: A dictionary containing the parsed information.
        """
        parts = title.split('\n')
        parsed_title = parts[0] if parts else title
        
        size_match = re.search(r'💾\s*([\d.]+)\s*(GB|MB)', title)
        peers_match = re.search(r'👤\s*(\d+)', title)
        
        size_in_gb = 0
        if size_match:
            size = float(size_match.group(1))
            unit = size_match.group(2)
            size_in_gb = size if unit == 'GB' else round(size / 1024, 2)
        
        peers = int(peers_match.group(1)) if peers_match else 0
        
        return {
            'title': parsed_title,
            'size_in_gb': size_in_gb,
            'peers': peers
        }
