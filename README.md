# chain-extractor

Chain extractor is a simple program that connects to a locally running cryptocurrency node and continuously fetches the new blocks from the node along with the address of each transaction. The extracted data can be stored in MongoDB (can be changed for other forms of database).

## Usage 

First install the dependencies:

```bash
pip install -r requirements.txt
```

Then setup configuration similar to the one provided in `env.example`, launch your mongodb instance and finally run the main entry point `update_storage.py`.

## TODO

* Automated scripts or docker to run on out of the box
* Add other metrics that can be extracted

