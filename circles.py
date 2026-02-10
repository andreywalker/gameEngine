import math

class Color:
    def __init__(self, r, g, b):
        self.r=r
        self.g=g
        self.b=b

    def __str__(self):
        return str(self.r)+","+str(self.g)+","+str(self.b)

    
class Vector:

    def __init__(self, x, y, z):
        self.x=x
        self.y=y
        self.z=z
    
    @classmethod
    def ZERO(cls):
        return cls(0, 0, 0)

    def dot(self, vector2):
        return self.x*vector2.x + self.y*vector2.y + self.z*vector2.z
    
    def __sub__(self, vector2):
        return Vector(self.x-vector2.x, self.y-vector2.y, self.z-vector2.z)
    def __str__(self):
        return str(self.x)+","+str(self.y)+","+str(self.z)
    

class Circle():
    def __init__(self, center:Vector, radius, color:Color):
        self.center=center
        self.radius=radius
        self.color=color

    def intersect_ray(self, ray_vector: Vector):
        print(self.center, ray_vector)
        oc =Vector.ZERO() - self.center

        a = ray_vector.dot(ray_vector)
        b = 2*oc.dot(ray_vector)
        c = oc.dot(oc) - self.radius*self.radius

        discriminant = b*b - 4*a*c
        if discriminant < 0:
            return None

        t1 = (-b + math.sqrt(discriminant)) / (2*a)
        t2 = (-b - math.sqrt(discriminant)) / (2*a)
        return min(t1, t2)
                