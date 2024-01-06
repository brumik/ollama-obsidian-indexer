# Obsidian Ollama Chat Indexer


## Requirements:

* ollama running on `localhost:11434`
* you shoud have installed a model (like 'mistral')

## Manual run with python3

* `python -m venv .venv`
* `source .venv/bin/activate`
* `pip install -r requirements.txt`
* `cp .env.sample .env`
* Fill out the env file to your liking
* `python index.py`

