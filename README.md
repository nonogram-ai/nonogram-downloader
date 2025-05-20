# Nonogram Downloader API

A containerized API for downloading nonogram puzzles from webpbn.com and nonograms.org in NON or XML format.

## Features

- Download nonogram puzzles from webpbn.com and nonograms.org by ID
- Support for both NON and XML formats
- Get puzzles as downloadable files or as plain text
- Optionally include solutions
- Deployed as a container for easy usage and deployment
- Browser automation for scraping puzzles from nonograms.org

## API Endpoints

- `GET /`: API information
- `GET /download/{puzzle_id}`: Download a puzzle as a file
  - Query parameters:
    - `source`: String (default: "webpbn", options: "webpbn" or "nonograms_org")
    - `format`: String (default: "non", options: "non" or "xml")
    - `include_solution`: Boolean (default: false)
- `GET /puzzle/{puzzle_id}/content`: Get puzzle content as text
  - Query parameters:
    - `source`: String (default: "webpbn", options: "webpbn" or "nonograms_org")
    - `format`: String (default: "non", options: "non" or "xml")
    - `include_solution`: Boolean (default: false)

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the API

1. Build and start the container:

```bash
docker-compose up -d
```

2. Access the API at http://localhost:8000

3. Visit http://localhost:8000/docs for interactive API documentation

### Without Docker

If you prefer to run the API without Docker:

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install chromium
```

3. Run the API:

```bash
uvicorn app:app --reload
```

## Example Usage

### Using curl

Download a puzzle from webpbn.com in NON format:
```bash
curl -o puzzle.non "http://localhost:8000/download/123"
```

Download a puzzle from nonograms.org in NON format:
```bash
curl -o puzzle.non "http://localhost:8000/download/123?source=nonograms_org"
```

Download a puzzle in XML format:
```bash
curl -o puzzle.xml "http://localhost:8000/download/123?format=xml"
```

Download a puzzle from nonograms.org in XML format:
```bash
curl -o puzzle.xml "http://localhost:8000/download/123?source=nonograms_org&format=xml"
```

Get puzzle content as text:
```bash
curl "http://localhost:8000/puzzle/123/content"
```

Get puzzle content in XML format:
```bash
curl "http://localhost:8000/puzzle/123/content?format=xml"
```

Include solution:
```bash
curl "http://localhost:8000/download/123?include_solution=true"
```

Download from nonograms.org with solution in XML format:
```bash
curl "http://localhost:8000/download/123?source=nonograms_org&format=xml&include_solution=true"
```

Get puzzle content:
```bash
curl "http://localhost:8000/puzzle/123/content"
```

Include solution:
```bash
curl "http://localhost:8000/download/123?include_solution=true"
```

Download from nonograms.org with solution:
```bash
curl "http://localhost:8000/download/123?source=nonograms_org&include_solution=true"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
