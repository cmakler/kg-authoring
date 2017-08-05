import uuid


class CurveData:
    def __init__(self, curve_data_def):
        type = curve_data_def['type']
        data_def = curve_data_def['def']
        if type == 'levelSetThroughPoint':
            self.data_object = LevelSetThroughPoint(data_def)


class MathFunction:
    def __init__(self, fn_def):
        self.fn_def = fn_def


class UnivariateFunction(MathFunction):
    def to_json(self):
        return {
            "fn": self.fn_def['fn'],
            "ind": self.fn_def['ind']
        }


class MultivariateFunction(MathFunction):
    def level_set(self, point):
        return []


class CobbDouglasFunction(MultivariateFunction):

    def value(self, point):
        alpha = str(self.fn_def['alpha'])
        return '((%s)^(%s))*((%s)^(1 - %s))' % (point[0], alpha, point[1], alpha)

    def level_set(self, level):
        alpha = str(self.fn_def['alpha'])
        return [
            UnivariateFunction({"fn": "((%s)/y^(1 - %s))^(1/%s)" % (level, alpha, alpha), "ind": "y"}),
            UnivariateFunction({"fn": "((%s)/x^(%s))^(1/(1 - %s))" % (level, alpha, alpha), "ind": "x"})
        ]

    def level_set_through_point(self, point):
        return self.level_set(self.value(point))


class LevelSetThroughPoint:
    def __init__(self, data_def):
        self.point = data_def['point']
        fn = data_def['fn']
        if fn['type'] == 'CobbDouglas':
            self.fn = CobbDouglasFunction(fn['def'])
        univariate_functions = self.fn.level_set_through_point(self.point)
        self.univariate_functions = [uf.to_json() for uf in univariate_functions]
