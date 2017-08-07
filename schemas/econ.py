from schemas.schema_parser import *


class EconAuthoringObjects(SchemaParser):
    def __init__(self, author_json):
        super(EconAuthoringObjects, self).__init__(author_json)
        self.special_types = ['budgetLine', 'indifferenceCurve', 'indifferenceMap']

    def handle_special_type(self, obj):
        obj_type = obj.get('type')
        obj_def = obj.get('def')
        if obj_type == 'budgetLine':
            return BudgetLine(obj_def).to_json()
        elif obj_type == 'indifferenceCurve':
            return IndifferenceCurve(obj_def).to_json()
        elif obj_type == 'indifferenceMap':
            return indifferenceMap(obj_def).to_json()
        else:
            return obj


class EconAuthoringObject:
    def __init__(self, obj_def):
        self.obj_def = obj_def


class BudgetLine(EconAuthoringObject):
    def to_json(self):
        d = self.obj_def
        m = str_var(d['m'])
        p1 = str_var(d['p1'])
        p2 = str_var(d['p2'])
        x_intercept = divide_strs(m, p1)
        y_intercept = divide_strs(m, p2)

        budget_segment = {
            'type': 'segment',
            'def': {
                'a': [x_intercept, 0],
                'b': [0, y_intercept],
                'stroke': 'green',
                'strokeWidth': 2,
                'label': 'BL',
                'drag': []
            }
        }
        if d.get('draggable'):
            budget_segment['def']['drag'].append({
                'directions': 'xy',
                'param': param_name(d['m']),
                'expression': 'drag.x*' + p1 + ' + drag.y*' + p2
            })
        if d.get('handles'):
            x_intercept_handle = {
                'type': 'point',
                'def': {
                    'coordinates': [x_intercept, 0],
                    'fill': 'green',
                    'r': 4,
                    'drag': [{
                        'directions': 'x',
                        'param': param_name(d['p1']),
                        'expression': m + '/drag.x'
                    }]
                }
            }
            y_intercept_handle = {
                'type': 'point',
                'def': {
                    'coordinates': [0, y_intercept],
                    'fill': 'green',
                    'r': 4,
                    'drag': [{
                        'directions': 'y',
                        'param': param_name(d['p2']),
                        'expression': m + '/drag.y'
                    }]
                }
            }
            return [budget_segment, x_intercept_handle, y_intercept_handle]
        else:
            return budget_segment


class IndifferenceCurve(EconAuthoringObject):
    def to_json(self):
        d = self.obj_def
        if d.get('map'):
            stroke_width = 1
            stroke = 'lightgrey'
        else:
            stroke_width = 2
            stroke = 'purple'
        label = d.get('label') or 'U'
        utility_type = d.get('utilityFunction').get('type')
        if utility_type == 'Complements' or utility_type == 'PerfectComplements':
            d['utilityFunction']['type'] = 'Min'
        if utility_type == 'Substitutes' or utility_type == 'PerfectSubstitutes':
            d['utilityFunction']['type'] = 'Linear'

        curve = {
            'type': 'curve',
            'def': {
                'data': {
                    'type': 'levelSet',
                    'def': {
                        'point': d.get('point'),
                        'level': d.get('level'),
                        'fn': d['utilityFunction']
                    }
                },
                'strokeWidth': stroke_width,
                'stroke': stroke,
                'label': label
            }
        }

        return curve


class indifferenceMap(EconAuthoringObject):
    def to_json(self):
        d = self.obj_def
        d['map'] = True

        objs = []

        for level in d['levels']:
            if type(level) is list:
                d['point'] = level
                objs.append({
                    'type': 'point',
                    'def': {
                        'coordinates': d['point'],
                        'fill': 'lightgrey',
                        'r': 3
                    }
                })
            else:
                d['level'] = level
            objs.append(IndifferenceCurve(d).to_json())

        return objs
