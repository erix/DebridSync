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
# Content Fetcher

Content Fetcher is a Python application that fetches watchlists from various content providers, searches for releases using configured indexers, and adds the found content to Real-Debrid for downloading.

## Features

- Supports multiple content providers (currently Trakt and Plex)
- Uses indexers to find releases (currently supports Torrentio)
- Integrates with Real-Debrid for downloading
- Configurable quality profiles
- Periodic checking for new watchlist items

## Configuration

The application is configured using a `config.yml` file. Here's an overview of the main configuration sections:

### Content Providers

Configure the content providers you want to use. Currently supported:

- Trakt
- Plex

### Indexers

Configure the indexers to use for finding releases. Currently supported:

- Torrentio

### Real-Debrid

Configure your Real-Debrid API token.

### Quality Profile

Set your preferred resolutions for content.

### Logging

Configure logging level and format.

### Developer Options

Enable/disable dry run mode for testing.

### Watchlist Management

Configure how often to check for new items and whether to remove items from the watchlist after processing.

## Usage

1. Clone the repository
2. Install dependencies using Poetry
3. Copy `config.yml.sample` to `config.yml` and edit it according to your needs
4. Run the application using `poetry run python src/main.py`

## Development

This project uses Poetry for dependency management. To set up a development environment:

1. Install Poetry
2. Run `poetry install` to install dependencies
3. Use `poetry run` to run commands within the virtual environment
