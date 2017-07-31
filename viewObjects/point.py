class Point(object):
    def __init__(self, name, x, y):
        self.x = x
        self.y = y
        self.z = self.x + self.y
