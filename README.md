# Obsidian Ollama Chat Indexer

This repo is the backend part for the Obsidian plugin found here: https://github.com/brumik/obsidian-ollama-chat

## Requirements:

* ollama running on `localhost:11434` (or other reachable url) - read further: https://ollama.ai/
* you shoud have installed a model (like 'mistral')

## Manual run with python3

* `python -m venv .venv`
* `source .venv/bin/activate`
* `pip install -r requirements.txt`
* `cp .env.sample .env`
* Fill out the env file to your liking
* `python index.py`

## Further developemnt

I am looking into ways how to create a Dockerfile and copmose file that sets
up the python app for you but I am running into problems with networking. If 
you are a docker virtuoso I am happy to accept your help. 

Further I am planning to look into how to deploy as an executable but python
is not my main language so any recommendations are welcome. 

Feel free to open an issue if you run into one or you would like to see a feature.

## Do you like what you see?

As every programmer I convert coffee to code:

<a href="https://www.buymeacoffee.com/brumik" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
