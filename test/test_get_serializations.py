

from tiddlyweb.config import config
from tiddlyweb.model.recipe import Recipe
from tiddlywebplugins.docs import Serialization

def setup_module(module):
    module.environ = {'tiddlyweb.config': config}
    module.serialization = Serialization(environ=module.environ)

def test_get_serializations():
    assert len(serialization.serializations) == 3

def test_get_serializations_recipe():

    assert len(serialization._matches('recipe_as')) == 3

    recipe = Recipe('hello')
    recipe.set_recipe([('barney', '')])

    output = serialization.recipe_as(recipe)
    assert 'tiddlyweb.serializations.json' in ''.join(list(output))
    

