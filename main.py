from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
from flask import jsonify
import math
ELASTIC_PASSWORD = "1234" # Change this to your own password here

es = Elasticsearch("https://localhost:9200",
                   http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    # return render_template('index.html')


@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword')
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no-1),
        'query': {
            'multi_match': {
                'query': keyword,
                'fields': ['title', 'lyrics']
            }
        }
    }
    res = es.search(index='lyrics', body=body)
    hits = [{'title': doc['_source']['title'],
             '_score': doc['_score'],
            'lyrics': (doc['_source']['lyrics'][:500] + "...." if len(doc['_source']['lyrics']) > 500 else doc['_source']['lyrics']), 'id': doc['_source']['id'],
              'image_url': doc['_source']['image_url']}
            for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value']/page_size)
    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)


@app.route('/song/<song_id>')
def song(song_id):
    body = {
        "query": {
        "term" : {
                "id": song_id
                }
        }
    }

    res = es.search(index='lyrics', body=body)

    for doc in res['hits']['hits']:
        hits = {'title': doc['_source']['title'],
                '_score': doc['_score'],
                'lyrics': doc['_source']['lyrics'],
                'image_url': doc['_source']['image_url']}
    
    # return render_template('song.html', hits=hits)
    return render_template('song.html', hits=hits)

@app.route('/autocomplete')
def autocomplete():
    search_term = request.args.get('q', '')
    body = {
        "size": 5,
        "query": {
            "multi_match": {
                "query": search_term,
                "fields": ["title^5", "lyrics"],
                "type": "phrase_prefix"
            }
        }
    }
    res = es.search(index='lyrics', body=body)
    suggestions = [{'title': doc['_source']['title'],'image_url': doc['_source']['image_url'], 'lyrics': doc['_source']['lyrics'], 'id': doc['_source']['id']} for doc in res['hits']['hits']]
    return jsonify(suggestions)

@app.route('/top')
def top():
    return render_template('topsong.html')


@app.route('/random')
def random():
    return render_template('randomsong.html')


# @app.route('/song')
# def song():
#     return render_template('song.html')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run()

