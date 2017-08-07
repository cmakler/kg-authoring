import uuid


class CurveData:
    def __init__(self, curve_data_def):
        type = curve_data_def['type']
        data_def = curve_data_def['def']
        if type == 'levelSetThroughPoint':
            self.data_object = LevelSetThroughPoint(data_def).curveData


class MathFunction:
    def __init__(self, fn_def):
        self.fn_def = fn_def


class UnivariateFunction(MathFunction):
    def to_json(self):
        keys = ['fn', 'ind', 'min', 'max', 'samplePoints']
        json = {
            'ind': 'x'
        }
        for key in keys:
            if self.fn_def.get(key):
                json[key] = self.fn_def.get(key)
        return json


class MultivariateFunction(MathFunction):
    def __init__(self, fn_def):
        super(MultivariateFunction, self).__init__(fn_def)
        if 'alpha' in fn_def.keys():
            fn_def['exponents'] = fn_def['coefficients'] = [fn_def['alpha'], '1 - ' + str(fn_def['alpha'])]
        if 'exponents' in fn_def.keys():
            self.exponents = [str(e) for e in fn_def['exponents']]
        if 'coefficients' in fn_def.keys():
            self.coefficients = [str(e) for e in fn_def['coefficients']]

    def level_set(self, point):
        return []

    def value(self, point):
        return 0

    def level_set_through_point(self, point):
        return self.level_set(self.value(point))


class CobbDouglasFunction(MultivariateFunction):
    def value(self, point):
        v = []
        for inx, p in enumerate(point):
            v.append('(%s)^(%s)' % (p, self.exponents[inx]))
        return '*'.join(v)

    def level_set(self, level):
        a = self.exponents[0]
        b = self.exponents[1]
        return [
            UnivariateFunction({
                "fn": "(%s/y^(%s))^(1/(%s))" % (level, b, a),
                "ind": "y",
                "min": "(%s)^(1/(%s + %s))" % (level, a, b)
            }),
            UnivariateFunction({
                "fn": "(%s/x^(%s))^(1/(%s))" % (level, a, b),
                "ind": "x",
                "min": "(%s)^(1/(%s + %s))" % (level, a, b)
            })
        ]


class Linear(MultivariateFunction):
    def value(self, point):
        p = ', '.join(map(str, point))
        c = ', '.join(map(str, self.coefficients))
        return 'multiply([%s],[%s])' % (p, c)

    def level_set(self, level):
        a = self.coefficients[0]
        b = self.coefficients[1]
        return [
            UnivariateFunction({
                "fn": "(%s - (%s)*y)/(%s)" % (level, b, a),
                "ind": "y",
                "samplePoints": 2
            }),
            UnivariateFunction({
                "fn": "(%s - (%s)*x)/(%s)" % (level, a, b),
                "ind": "x",
                "samplePoints": 2
            }),
        ]


class Min(MultivariateFunction):
    def value(self, point):
        v = []
        for inx, p in enumerate(point):
            v.append('(%s)*(%s)' % (p, self.exponents[inx]))
        minimands = ','.join(v)
        return '(min(%s)' % minimands

    def level_set(self, level):
        a = self.coefficients[0]
        b = self.coefficients[1]
        return [
            UnivariateFunction({
                "fn": "%s/(%s)" % (level, b),
                "ind": "x",
                "min": "%s/(%s)" % (level, a),
                "samplePoints": 2
            }),
        ]


class LevelSetThroughPoint:
    def __init__(self, data_def):
        self.point = data_def['point']
        fn = data_def['fn']
        if fn['type'] == 'CobbDouglas':
            self.fn = CobbDouglasFunction(fn['def'])
            interpolation = 'curveMonotoneX'
        if fn['type'] == 'Min':
            self.fn = Min(fn['def'])
            interpolation = 'curveLinear'
        if fn['type'] == 'Linear':
            self.fn = Linear(fn['def'])
            interpolation = 'curveLinear'
        univariate_functions = self.fn.level_set_through_point(self.point)
        self.curveData = [{'univariateFunction': uf.to_json(), 'interpolation': interpolation} for uf in
                          univariate_functions]
