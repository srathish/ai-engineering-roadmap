# Week 4 — Git, GitHub and APIs

A command-line weather tool that calls a real public REST API using the `requests` library.

## What it does
- `weather_cli.py` — asks for a city name, looks up its coordinates with the free Open-Meteo geocoding API, then fetches the current weather for those coordinates. It prints the temperature, wind speed and conditions. No API key is needed. Network errors, timeouts and unknown cities are all handled gracefully instead of crashing.

## How to run
First install the one dependency:
```
pip3 install -r requirements.txt
```
Then run it, either interactively or by passing the city as an argument:
```
python3 weather_cli.py
python3 weather_cli.py London
```

## What I learned
- I learned the basics of git and GitHub for tracking my work: initializing a repo, committing changes, and pushing to a remote so the project is backed up and shareable.
- I learned how to call a REST API over HTTP using the `requests` library and read the JSON response.
- I learned how an API can take query parameters, and how to chain two calls together — first geocoding the city, then fetching its weather.
- I learned how to handle network problems with `try`/`except`, catching timeouts and connection errors separately so the program fails clearly.
- I learned to check for an empty result (a city that doesn't exist) before trying to use the data.
- I learned how to read command-line arguments with `sys.argv` so the tool can be run interactively or scripted.
- I learned to keep dependencies in a `requirements.txt` file so anyone can install what the project needs.
