# BioGRID Biorxiv Fetcher
Take a list of BioRxiv DOIs and parse them out using the BioRxiv API

## Requirements
+ Pipenv (https://pypi.org/project/pipenv/)
+ Python 3.6.9 (https://www.python.org/)

## Configuration
+ You need to create a new file called `config/config.yml` containing the settings for your implementation. You can use the `config/config.sample.yml` file as a template.

## How to Run
+ Go into the directory containing this repository
+ Run: `pipenv shell`
+ Run: `pipenv install`
+ Create a directory called `<DOWNLOAD_PATH>` (what you set `download_path` equal to in the config file)
+ Run: `python run.py -i `<input_file>` -o `<output_file>` -e `<excel_file>` -s `<start id>` where `<start id>` is replaced with the id you want to start counting from. So using `125` would start counting from `888800000125`.
+ Running this script will will create a file called `<output_file>` and another file called `<excel_file>` in the `<DOWNLOAD_PATH>` folder