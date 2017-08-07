from schemas.schema_parser import *


class EconAuthoringObjects(SchemaParser):
    def __init__(self, author_json):
        super(EconAuthoringObjects, self).__init__(author_json)
        self.special_types = ['budgetLine', 'indifferenceCurve']

    def handle_special_type(self, obj):
        obj_type = obj.get('type')
        obj_def = obj.get('def')
        if obj_type == 'budgetLine':
            return BudgetLine(obj_def).to_json()
        elif obj_type == 'indifferenceCurve':
            return IndifferenceCurve(obj_def).to_json()
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
        utility_type = d.get('utilityFunction').get('type')
        if utility_type == 'Complements' or utility_type == 'PerfectComplements':
            d['utilityFunction']['type'] = 'Min'
        if utility_type == 'Substitutes' or utility_type == 'PerfectSubstitutes':
            d['utilityFunction']['type'] = 'Linear'
        data = {}
        if d.get('point'):
            data = {
                'type': 'levelSetThroughPoint',
                'def': {
                    'point': d['point'],
                    'fn': d['utilityFunction']
                }
            }
        elif d.get('level'):
            data = {
                'type': 'levelSet',
                'def': {
                    'level': d['level'],
                    'fn': d['utilityFunction']
                }
            }
        else:
            print('need to define an indifference curve either by a level or a point')

        curve = {
            'type': 'curve',
            'def': {
                'data': data,
                'strokeWidth': 2,
                'stroke': 'purple',
                'label': 'U'
            }
        }

        return curve
