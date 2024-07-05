import requests
from typing import List, Dict, Literal
from .release_finder import ReleaseFinder

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
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            
            releases = []
            for stream in data.get('streams', []):
                release = {
                    'title': stream.get('title', ''),
                    'infoHash': stream.get('infoHash', '')
                }
                releases.append(release)
            
            return releases
        
        except requests.RequestException as e:
            print(f"Error fetching data from Torrentio: {e}")
            return []
