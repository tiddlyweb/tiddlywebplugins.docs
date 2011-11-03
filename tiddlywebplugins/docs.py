"""
Autogenerate TiddlyWeb API docs via a serialization.
"""

from tiddlyweb.serializer import (Serializer, NoSerializationError,
        TiddlerFormatError, BagFormatError, RecipeFormatError)
from tiddlyweb.serializations import SerializationInterface
from tiddlywebplugins.templates import get_template


__version__ = '0.3'


EXTENSION_TYPES = {
        'x-doc': 'text/x-tiddlyweb-docs'
        }


SERIALIZERS = {
        'text/x-tiddlyweb-docs': ['tiddlywebplugins.docs',
            'text/html; charset=UTF-8'],
        }


def init(config):
    if 'selector' in config:
        config['extension_types'].update(EXTENSION_TYPES)
        config['serializers'].update(SERIALIZERS)


class Serialization(SerializationInterface):

    def __init__(self, environ=None):
        SerializationInterface.__init__(self, environ)
        self.extensions = {}
        self.serializations = []
        self._build_serializers()

    # XXX surely I can dry this up?
    def recipe_as(self, recipe):
        return self._all_info('recipe_as', 'as_recipe')

    def bag_as(self, bag):
        return self._all_info('bag_as', 'as_bag')

    def tiddler_as(self, tiddler):
        return self._all_info('tiddler_as', 'as_tiddler')

    def list_recipes(self, recipes):
        return self._all_info('list_recipes')

    def list_bags(self, bags):
        return self._all_info('list_bags')

    def list_tiddlers(self, tiddlers):
        return self._all_info('list_tiddlers')

    def _build_serializers(self):
        try:
            for extension, mime in (self.environ['tiddlyweb.config']
                    ['extension_types'].iteritems()):
                self.extensions[mime] = extension
            for mime, outputter in (self.environ['tiddlyweb.config']
                    ['serializers'].iteritems()):
                module, _ = outputter
                if module == __name__ or mime == 'default':
                    continue
                self.serializations.append((self.extensions[mime],
                        Serializer(module, self.environ).serialization))
        except KeyError:
            pass

    def _matches(self, method):
        matches = []
        for serialization in self.serializations:
            if hasattr(serialization[1], method):
                matches.append(serialization)
        return matches

    def _all_info(self, out_method, in_method=None):
        method_info = self._method_info()
        out_serialization_info = self._serialization_info(out_method)
        if in_method and 'PUT' in method_info['method']:
            in_serialization_info = self._serialization_info(in_method)
        else:
            in_serialization_info = {}

        template = get_template(self.environ, 'tiddlywebdocs.html')
        return template.generate({'outserialization': out_serialization_info,
            'inserialization': in_serialization_info,
            'method': method_info})

    def _serialization_info(self, method):
        serializers = self._matches(method)
        info = {}
        for serializer in serializers:
            try:
                try:
                    getattr(serializer[1], method)([])
                except TypeError:
                    getattr(serializer[1], method)('', '')
            except NoSerializationError:
                continue
            except (AttributeError, TiddlerFormatError, BagFormatError,
                    RecipeFormatError):
                pass  # wow!
            info[serializer[1].__module__] = {
                    'doc': getattr(serializer[1], method).__doc__,
                    'ext': serializer[0]}
        return info

    def _method_info(self):
        methods = self.environ.get('selector.methods', [])
        path = self.environ.get('SCRIPT_NAME', 'Unavailable')
        matched_path = self.environ.get('selector.matches', [path])[0]

        selector = self.environ['tiddlyweb.config'].get('selector', None)
        if '.x-doc' in path:
            cleanpath = path.rsplit('.x-doc')[0]
        else:
            cleanpath = path
        query_string = self.environ.get('QUERY_STRING', '')
        if query_string:
            query_string = '?%s' % query_string
        info = {'path': path, 'cleanpath': cleanpath, 'method': {},
                'query': query_string}

        if selector:
            for method in sorted(methods):
                handler = selector.select(matched_path, method)[0]
                info['method'][method] = ('%s:%s' % (handler.__module__,
                    handler.__name__), '%s' % handler.__doc__)

        return info
