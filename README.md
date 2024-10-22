# DebridSync

**Note: This project is currently under heavy development and is not yet intended for general usage.**

DebridSync is a Python application that fetches watchlists from various content providers (such as Trakt and Plex), finds releases for the items in the watchlist using torrent indexers (like Torrentio), and adds the best quality releases to a debrid service (currently supporting Real-Debrid).

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
# Watchlists
watchlists:
    trakt:
        user:
            - watchlist
            - collection
            - favorites
        public:
            - user1/list-id-1
            - user2/list-id-2
    plex:
        - watchlist


# Media Library
media_library:
  plex_libraries:
    - Movies
    - TV Shows
  trakt_collection: true
  real_debrid: true

# Plex
plex:
  server_url: http://your-plex-server:32400
  token: YOUR_PLEX_TOKEN_HERE

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
  check_interval: 3600  # Check for new items every hour (in seconds)
```

Create a `.env` file in the project root with the following content:

```
TRAKT_CLIENT_ID=your_trakt_client_id
TRAKT_CLIENT_SECRET=your_trakt_client_secret
```

## Usage

### Running locally

To run the application locally:

```
python src/main.py
```

### Running with Docker

1. Build the Docker image:
   ```
   docker build -t debridsync .
   ```

2. Run the Docker container:
   ```
   docker run -v $(pwd):/app debridsync
   ```

This will run the DebridSync application in a Docker container, using the `config.yml` and `.env` files from your local directory.

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
