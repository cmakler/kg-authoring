from parsers.math import *


class AuthoringObject:
    def __init__(self, object_def, key=''):
        self.objectDef = object_def
        self.name = str(uuid.uuid4())
        self.key = key
        self.sub_objects = self.create_sub_objects()

    def create_sub_objects(self):
        return []

    def get_defs(self, keys=[]):
        result = {}
        for key in keys:
            if key in self.objectDef.keys():
                result[key] = self.objectDef[key]
        return result

    def to_json(self, export_json):

        if self.key in export_json.keys():
            export_json[self.key] = self.objectDef

        for obj in self.sub_objects:
            obj.to_json(export_json)


class Graph(AuthoringObject):
    def create_sub_objects(self):

        x_scale = Scale({
            'dim': 'x',
            'domain': self.objectDef['xAxis']['domain'],
            'range': self.objectDef['xAxis']['range']
        })

        y_scale = Scale({
            'dim': 'y',
            'domain': self.objectDef['yAxis']['domain'],
            'range': self.objectDef['yAxis']['range']
        })

        names = {
            'xScaleName': x_scale.name,
            'yScaleName': y_scale.name
        }

        clip_path = ClipPath(names)

        sub_objects = [x_scale, y_scale, clip_path]

        if 'xAxis' in self.objectDef.keys():
            x_axis_def = self.objectDef['xAxis']
            x_axis_def.update(names)
            sub_objects.append(Axis(x_axis_def))

        if 'yAxis' in self.objectDef.keys():
            y_axis_def = self.objectDef['yAxis']
            y_axis_def.update(names)
            sub_objects.append(Axis(y_axis_def))

        names['clipPathName'] = clip_path.name

        for obj in self.objectDef['objects']:
            obj['def'].update(names)
            if obj['type'] == 'segment':
                sub_objects.append(Segment(obj['def']))
            if obj['type'] == 'curve':
                sub_objects.append(Curve(obj['def']))
            if obj['type'] == 'point':
                sub_objects.append(Point(obj['def']))

        return sub_objects


class Slider(AuthoringObject):
    def create_sub_objects(self):

        d = self.objectDef

        x_scale = Scale({
            'dim': 'x',
            'domain': d['domain'],
            'range': [d['x'], d['x']+d['width']]
        })

        y_scale = Scale({
            'dim': 'y'
        })

        if d.get('noAxis'):

            return [x_scale, y_scale, Label({
                'xScaleName': x_scale.name,
                'yScaleName': y_scale.name,
                'coordinates': [d['domain'][0], d['y']],
                'text': '`%s = ${params.%s.toFixed(2)}`' % (d['paramLabel'], d['param']),
                'drag': [{
                    'directions': 'x',
                    'param': d['param'],
                    'expression': 'params.%s + drag.dx' % d['param']
                }]
            })]

        else:

            axis = Axis({
                'xScaleName': x_scale.name,
                'yScaleName': y_scale.name,
                'intercept': d['y'],
                'orient': 'bottom',
                'ticks': 2
            })

            point = Point({
                'xScaleName': x_scale.name,
                'yScaleName': y_scale.name,
                'coordinates': ['params.%s' % d['param'], d['y']],
                'drag': [{
                    'directions': 'x',
                    'param': d['param'],
                    'expression': 'params.%s + drag.dx' % d['param']
                }]
            })

            label = Label({
                'xScaleName': x_scale.name,
                'yScaleName': y_scale.name,
                'coordinates': [d['domain'][1], d['y']],
                'xPixelOffset': 20,
                'yPixelOffset': -10,
                'text': '`%s = ${params.%s.toFixed(2)}`' % (d['paramLabel'], d['param']),
                'drag': [{
                    'directions': 'x',
                    'param': d['param'],
                    'expression': 'params.%s + drag.dx' % d['param']
                }]
            })

        return [x_scale, y_scale, axis, point, label]


class Scale(AuthoringObject):
    def to_json(self, parsed):
        json = {
            'name': self.name
        }
        if self.objectDef.get('domain'):
            json.update({
                'domainMin': str(self.objectDef.get('domain')[0]),
                'domainMax': str(self.objectDef.get('domain')[1]),
            })
        else:
            json.update({
                'domainMin': '0',
                'domainMax': '1',
            })
        if self.objectDef.get('range'):
                json.update({
                    'rangeMin': str(self.objectDef.get('range')[0]),
                    'rangeMax': str(self.objectDef.get('range')[1]),
                })
        else:
                json.update({
                    'rangeMin': '0',
                    'rangeMax': '1',
                })
        if self.objectDef['dim'] == 'x':
            parsed['xScales'].append(json)
        else:
            parsed['yScales'].append(json)


class GraphObject(AuthoringObject):
    def get_defs(self, keys=[]):
        keys = list(set(keys + ['xScaleName', 'yScaleName']))
        return super(GraphObject, self).get_defs(keys)

    def extract_coordinates(self, graph_info, coords_key='coordinates', x_key='x', y_key='y'):
        graph_info[x_key] = str(self.objectDef[coords_key][0])
        graph_info[y_key] = str(self.objectDef[coords_key][1])


class Axis(GraphObject):
    def to_json(self, parsed):
        json = self.get_defs(['orient', 'title', 'ticks', 'intercept'])
        parsed['axes'].append(json)


class ClipPath(GraphObject):
    def to_json(self, export_json):
        json = self.get_defs()
        json['name'] = self.name
        export_json['clipPaths'].append(json)


class Label(GraphObject):
    def to_json(self, export_json):
        json = self.get_defs(['clipPathName', 'text', 'fontSize', 'xPixelOffset', 'yPixelOffset','drag'])
        self.extract_coordinates(json)
        export_json['labels'].append(json)


class GeometricGraphObject(GraphObject):
    def get_defs(self, keys=[]):
        keys = list(set(keys + ['clipPathName', 'color', 'stroke', 'strokeWidth', 'fill', 'r']))
        return super(GeometricGraphObject, self).get_defs(keys)


class Segment(GeometricGraphObject):
    def to_json(self, parsed):
        json = self.get_defs(['clipPathName', 'drag'])
        self.extract_coordinates(json, 'a', 'x1', 'y1')
        self.extract_coordinates(json, 'b', 'x2', 'y2')
        parsed['segments'].append(json)


class Curve(GeometricGraphObject):
    def to_json(self, export_json):
        json = self.get_defs(['clipPathName', 'drag'])
        for curve_data in CurveData(self.objectDef['data']).data_object:
            curve_json = dict(json)
            curve_json.update(curve_data)
            export_json['curves'].append(curve_json)


class Point(GeometricGraphObject):
    def create_sub_objects(self):
        sub_objects = []
        if 'label' in self.objectDef.keys():
            label_def = self.objectDef['label']
            label_def.update(self.get_defs(['clipPathName', 'drag', 'coordinates']))
            label_def.update({
                'fontSize': '8',
                'xPixelOffset': '5',
                'yPixelOffset': '-15'
            })
            sub_objects.append(Label(label_def))
        return sub_objects

    def to_json(self, export_json):
        json = self.get_defs(['clipPathName', 'drag'])
        self.extract_coordinates(json)
        export_json['points'].append(json)
        for obj in self.sub_objects:
            obj.to_json(export_json)
