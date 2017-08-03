import uuid


class CurveData:
    def __init__(self, curve_data_def):
        type = curve_data_def['type']
        data_def = curve_data_def['def']
        if type == 'levelSetThroughPoint':
            self.data_object = LevelSetThroughPoint(data_def)


class MathFunction:
    def __init__(self, fn_def):
        self.name = str(uuid.uuid4())
        self.fn_def = fn_def

    def get_name(self):
        return self.name


class UnivariateFunction(MathFunction):
    def to_json(self, export_json):
        json = {
            "name": self.name,
            "fn": self.fn_def['fn'],
            "ind": self.fn_def['ind']
        }
        export_json['univariateFunctions'].append(json)


class MultivariateFunction(MathFunction):
    def level_set(self, point):
        return []


class CobbDouglasFunction(MultivariateFunction):
    def level_set(self, point):
        alpha = str(self.fn_def['alpha'])
        return [
            UnivariateFunction({"fn": "((%s)/x)^(%s/(1 - %s))*%s" % (point[0], alpha, alpha, point[1]), "ind": "x"}),
            UnivariateFunction({"fn": "((%s)/y)^((1 - %s)/(%s))*%s" % (point[1], alpha, alpha, point[0]), "ind": "y"})
        ]


class LevelSetThroughPoint:
    def __init__(self, data_def):
        self.point = data_def['point']
        fn = data_def['fn']
        if fn['type'] == 'CobbDouglas':
            self.fn = CobbDouglasFunction(fn['def'])
        self.univariate_functions = self.fn.level_set(self.point)
