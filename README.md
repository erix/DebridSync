# DebridSync

**Note: This project is currently under heavy development and is not yet intended for general usage.**

DebridSync is a Python application that fetches watchlists from various content providers (such as Trakt), finds releases for the items in the watchlist using torrent indexers (like Torrentio), and adds the best quality releases to a debrid service (currently supporting Real-Debrid).

## Features

- Fetch watchlists from Trakt
- Find releases using Torrentio
- Filter releases based on quality preferences
- Add selected releases to Real-Debrid
- Dry run mode for testing without making changes

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
    username: your_plex_username
    password: your_plex_password

# Release Finders
release_finders:
  torrentio:
    enabled: true
    # Add any Torrentio-specific settings here if needed

# Real-Debrid
real_debrid:
  api_token: YOUR_API_TOKEN_HERE

# Quality Profile
quality_profile:
  resolutions:
    - 2160p
    - 1080p
    - 720p

# Logging
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Developer Options
developer:
  dry_run: false
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
