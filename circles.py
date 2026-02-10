import math

class Color:
    def __init__(self, r, g, b):
        self.r=r
        self.g=g
        self.b=b

    def __str__(self):
        return str(self.r)+","+str(self.g)+","+str(self.b)
    def multiply(self, n):
        return Color(self.r*n, self.g*n, self.b*n)
    
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
    def multiply(self, n):
        return Vector(self.x*n, self.y*n, self.z*n)
    def __sub__(self, vector2):
        return Vector(self.x-vector2.x, self.y-vector2.y, self.z-vector2.z)
    def __add__(self, vector2):
        return Vector(self.x+vector2.x, self.y+vector2.y, self.z+vector2.z)
    def __str__(self):
        return str(self.x)+","+str(self.y)+","+str(self.z)
    def length(self):
        return math.sqrt(self.dot(self))

class Sphere():
    def __init__(self, center:Vector, radius, color:Color, specular):
        self.center=center
        self.radius=radius
        self.color=color
        self.specular = specular

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
    
class Light():
    def __init__(self, type, intensity, pos_dir=Vector(0, 0, 0)):
        self.type=type #ambient - 1, point - 2, dir - 3
        self.intensity=intensity
        self.pos_dir=pos_dir
                
                