"""
Make sure the web output is satisfactory.
"""

import os
import shutil

import httplib2

from wsgi_intercept import httplib2_intercept
import wsgi_intercept

from tiddlyweb.web.serve import load_app

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlywebplugins.utils import get_store
from tiddlyweb.config import config

def setup_module(module):
    if os.path.exists('store'):
        shutil.rmtree('store')
    store = get_store(config)

    recipe = Recipe('foobar')
    recipe.set_recipe([('something', '')])
    store.put(recipe)

    bag = Bag('something')
    store.put(bag)

    tiddler = Tiddler('fuss', 'something')
    tiddler.text = '!Hi'
    store.put(tiddler)

    def app_fn(): 
        return load_app()

    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8000, app_fn)

    module.http = httplib2.Http()


def test_recipes():
    response, content = http.request('http://0.0.0.0:8000/recipes.x-doc')
    _confirm_recipes(response, content)
    response, content = http.request('http://0.0.0.0:8000/recipes',
            headers={'Accept': 'text/x-tiddlyweb-docs'})
    _confirm_recipes(response, content)

def test_recipe():
    response, content = http.request('http://0.0.0.0:8000/recipes/foobar.x-doc')
    _confirm_recipe(response, content)
    response, content = http.request('http://0.0.0.0:8000/recipes/foobar',
            headers={'Accept': 'text/x-tiddlyweb-docs'})
    _confirm_recipe(response, content)

def test_recipe_tiddlers():
    response, content = http.request('http://0.0.0.0:8000/recipes/foobar/tiddlers.x-doc')
    _confirm_recipe_tiddlers(response, content)
    assert '<h1>/recipes/foobar/tiddlers.x-doc' in content
    response, content = http.request('http://0.0.0.0:8000/recipes/foobar/tiddlers',
            headers={'Accept': 'text/x-tiddlyweb-docs'})
    _confirm_recipe_tiddlers(response, content)
    assert '<h1>/recipes/foobar/tiddlers' in content

def test_recipe_tiddler():
    response, content = http.request('http://0.0.0.0:8000/recipes/foobar/tiddlers/fuss.x-doc')
    _confirm_recipe_tiddler(response, content)
    response, content = http.request('http://0.0.0.0:8000/recipes/foobar/tiddlers/fuss',
            headers={'Accept': 'text/x-tiddlyweb-docs'})
    _confirm_recipe_tiddler(response, content)

def _confirm_recipes(response, content):
    assert response['status'] == '200'
    assert 'text/html' in response['content-type']

    assert '<h2>methods' in content
    assert '<h2>output serializations' in content

    assert 'tiddlyweb.serializations.json' in content
    assert 'tiddlyweb.serializations.text' in content
    assert 'tiddlyweb.serializations.html' in content

    assert 'GET: ' in content
    assert 'PUT: ' not in content

def _confirm_recipe(response, content):
    assert response['status'] == '200'
    assert 'text/html' in response['content-type']

    assert '<h2>methods' in content
    assert '<h2>output serializations' in content
    assert '<h2>input serializations' in content

    assert 'tiddlyweb.serializations.json' in content
    assert 'tiddlyweb.serializations.text' in content
    assert 'tiddlyweb.serializations.html' in content

    assert 'GET: ' in content
    assert 'PUT: ' in content

def _confirm_recipe_tiddlers(response, content):
    assert response['status'] == '200'
    assert 'text/html' in response['content-type']

    assert '<h2>methods' in content
    assert '<h2>output serializations' in content

    assert 'tiddlyweb.serializations.json' in content
    assert 'tiddlyweb.serializations.text' in content
    assert 'tiddlyweb.serializations.html' in content

    assert 'foobar/tiddlers.html"' in content
    assert 'foobar/tiddlers.txt"' in content
    assert 'foobar/tiddlers.json"' in content

    assert 'GET: ' in content
    assert 'PUT: ' not in content

def _confirm_recipe_tiddler(response, content):
    assert response['status'] == '200'
    assert 'text/html' in response['content-type']

    assert '<h2>methods' in content
    assert '<h2>output serializations' in content
    assert '<h2>input serializations' in content

    assert 'tiddlyweb.serializations.json' in content
    assert 'tiddlyweb.serializations.text' in content
    assert 'tiddlyweb.serializations.html' in content

    assert 'foobar/tiddlers/fuss.html"' in content
    assert 'foobar/tiddlers/fuss.txt"' in content
    assert 'foobar/tiddlers/fuss.json"' in content

    assert 'GET: ' in content
    assert 'PUT: ' in content
