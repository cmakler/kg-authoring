from parsers.parser import *


def str_var(s):
    return '(' + s + ')'


def divide_strs(a, b):
    return a + '/' + b


def param_name(s):
    return s.replace('params.', '')


class SchemaParser:
    def __init__(self, author_json):
        self.author_json = author_json
        self.special_types = ['']

    def handle_special_type(self, obj):
        print('handling special type ' + obj.get('type'))
        return obj

    def to_authoring_json(self):
        def parse_json(json, parent=None):
            if type(json) is dict:
                if json.get('type') in self.special_types:
                    new_objs = self.handle_special_type(json)
                    if type(new_objs) is dict:
                        return new_objs
                    else:
                        for new_obj in new_objs:
                            if parent:
                                parent.append(new_obj)
                            else:
                                print('tried to append an array to nothing')
                else:
                    for obj in json:
                        json[obj] = parse_json(json[obj])
                return json
            elif type(json) is list:
                return [parse_json(obj, json) for obj in json]
            else:
                return json

        return parse_json(self.author_json)
