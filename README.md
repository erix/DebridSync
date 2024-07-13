# DebridSync

**Note: This project is currently under heavy development and is not yet intended for general usage.**

DebridSync is a Python application that fetches watchlists from various content providers (such as Trakt), finds releases for the items in the watchlist using torrent indexers (like Torrentio), and adds the best quality releases to a debrid service (currently supporting Real-Debrid).

## Features

- Fetch watchlists from various content providers (currently Trakt and Plex)
- Find releases using configured indexers (currently supports Torrentio)
- Filter and rank releases using [RTN (Rank Torrent Name)](https://github.com/dreulavelle/rank-torrent-name)
- Add selected releases to Real-Debrid
- Dry run mode for testing without making changes
- Periodic checking for new watchlist items

## Configuration

The application uses a YAML configuration file (`config.yml`) and environment variables for sensitive information. Here's an example configuration:

```yaml
# Content Providers
content_providers:
  trakt:
    enabled: true
    # Trakt client ID and secret are loaded from .env file
  plex:
    enabled: false
    token: YOUR_PLEX_SERVER_TOKEN_HERE
    server_url: YOUR_PLEX_SERVER_URL_HERE
    library_name: Movies

# Indexers
indexers:
  torrentio:
    enabled: true
    # Add any Torrentio-specific settings here if needed

# Real-Debrid
real_debrid:
  api_token: YOUR_API_TOKEN_HERE

# Torrent Settings
torrent_settings:
  require:
    - 1080p
    - 4K
  exclude:
    - CAM
    - TS
  preferred:
    - HDR
    - BluRay

# Ranking Model
ranking_model:
  uhd: 200
  hdr: 100
  # Add more attributes and scores as needed


# Logging
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Developer Options
developer:
  dry_run: false

# Watchlist Management
watchlist:
  remove_after_adding: false
  check_interval: 3600  # Check for new items every hour (in seconds)
```

Create a `.env` file in the project root with the following content:

```
TRAKT_CLIENT_ID=your_trakt_client_id
TRAKT_CLIENT_SECRET=your_trakt_client_secret
```

## Usage

To run the application:

```
python src/main.py
```

## Developer Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/debridsync.git
   cd debridsync
   ```

2. Install Poetry (if not already installed):
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Activate the virtual environment:
   ```
   poetry shell
   ```

5. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

6. Run tests:
   ```
   pytest
   ```

7. Run the application:
   ```
   python src/main.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
