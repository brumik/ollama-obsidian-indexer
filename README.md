# Obsidian Ollama Chat Indexer

This repo is the backend part for the Obsidian plugin found here: https://github.com/brumik/obsidian-ollama-chat

## Requirements:

- ollama running on `localhost:11434` (or other reachable url) - read further: https://ollama.ai/
- you shoud have installed a model (like 'mistral')

## Manual run with python3

The project is moved to poetry for easier packaging (on nix). I did not verified these steps but should work:

- `cp ./ollama_obsidian_indexer/.env.sample ./ollama_obsidian_indexer/.env`
- Fill out the env file to your liking
- `poetry install`
- `poetry run ./ollama_obsidian_indexer/index.py`

## Nix package:

The packet comes with nix devenv and compiles to nix package. To build it yourself you can run:

- `cp ./ollama_obsidian_indexer/.env.sample ./ollama_obsidian_indexer/.env`
- `nix build`

This will use the `.env` file that you have. I am figuring out how to define the env variables on runtime.

## Docker

The project ships with a `Dockerfile` and example `docker-compose.yml`. You may either pass your .env file into the container using the `env_file` directive, or set variables directly using `environment`

## Further developemnt

Further I am planning to look into how to deploy as an executable but python
is not my main language so any recommendations are welcome.

Feel free to open an issue if you run into one or you would like to see a feature.

## Do you like what you see?

As every programmer I convert coffee to code:

<a href="https://www.buymeacoffee.com/brumik" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
