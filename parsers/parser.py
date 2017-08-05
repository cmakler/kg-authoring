from parsers.authoring_objects import *
from schemas.econ import EconAuthoringObjects

KGJS = 'kgjs'


def parse(author, export_schema=KGJS):

    if author.get('schema') == 'econ':
        author = EconAuthoringObjects(author).to_authoring_json()

    authoring_objects = AuthoringObjects(author)

    # export according to the requested export_schema
    return authoring_objects.to_json(export_schema)


class AuthoringObjects:
    def __init__(self, author):
        self.authoring_objects = []
        for key in author:
            if key == 'graphs':
                for graph_def in author['graphs']:
                    self.authoring_objects.append(Graph(graph_def))
            else:
                self.authoring_objects.append(AuthoringObject(author[key], key))

    def to_json(self, export_schema=KGJS):

        export_json = {}

        if export_schema == KGJS:
            export_json.update({
                'aspectRatio': 1,
                'params': [],
                'restrictions': [],
                'xScales': [],
                'yScales': [],
                'clipPaths': [],
                'univariateFunctions': [],
                'segments': [],
                'curves': [],
                'axes': [],
                'points': [],
                'labels': []
            })

            for obj in self.authoring_objects:
                obj.to_json(export_json)

        return export_json
