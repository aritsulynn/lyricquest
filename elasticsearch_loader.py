# py .\elasticsearch_loader.py --file .\Datasource\out.csv --index lyrics

from elasticsearch import Elasticsearch, helpers
import ndjson
import argparse
import uuid
import csv
ELASTIC_PASSWORD = "1234" # Change this to your own password here
es = Elasticsearch( "https://localhost:9200", basic_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

parser = argparse.ArgumentParser()
parser.add_argument('--file', help='Path to the .csv file', required=True)
parser.add_argument('--index', help='The name of the Elasticsearch index', required=True)
args = parser.parse_args()

index = args.index
file_path = args.file

def csv_data(csv_file, _index):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield {
                "_index": _index,
                "_id": uuid.uuid4(),
                "_source": row
            }

def setting():
    # Close the index
    es.indices.close(index=index)

    # Set index settings
    settings_body = {
        "settings": {
            "index": {
                "similarity": {
                    "default": {
                        "type": "BM25",
                        "b": 0.75,
                        "k1": 1.2
                    }
                },
                "analysis": {
                    "analyzer": {
                        "lyrics_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding",
                                "english_possessive_stemmer",
                                "english_stop",
                                "english_stemmer"
                            ]
                        }
                    },
                    "filter": {
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english"
                        },
                        "english_stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                        },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        }
                    }
                }
            }
        }
    }

    es.indices.put_settings(index=index, settings=settings_body)

    # Open the index
    es.indices.open(index=index)

def delete_index():
    es.indices.delete(index=index, ignore=[400, 404])


try:
    delete_index()
    response = helpers.bulk(es, csv_data(file_path, index))
    setting()
    # delete_index()
    # print("\nRESPONSE:", response)
except Exception as e:
    print("\nERROR:", e)