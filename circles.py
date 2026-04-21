import math

class Color:
    def __init__(self, r, g, b):
        if r>255:
            r=255
        if g>255:
            g=255
        if b>255:
            b=255
        self.r=r
        self.g=g
        self.b=b

    def __str__(self):
        return str(self.r)+","+str(self.g)+","+str(self.b)
    
    def multiply(self, n):
        return Color(self.r*n, self.g*n, self.b*n)
    
    def __add__(self, color2):
        return Color(self.r+color2.r, self.g+color2.g, self.b+color2.b)
    
    def mix(self, reflected_color, reflective):
        contribution1 = self.multiply(1-reflective)
        contribution2=reflected_color.multiply(reflective)
        return contribution1+contribution2
    
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
    
    def normalize(self):
        l = self.length()
        return self.multiply(1/l)
    
    def apply_matrix(self, m):
        return Vector(
            m[0][0]*self.x + m[0][1]*self.y + m[0][2]*self.z,
            m[1][0]*self.x + m[1][1]*self.y + m[1][2]*self.z,
            m[2][0]*self.x + m[2][1]*self.y + m[2][2]*self.z
        )

class Sphere():
    def __init__(self, center:Vector, radius, color:Color, specular=50, reflective = 0.2):
        self.center=center
        self.radius=radius
        self.color=color
        self.specular = specular
        self.reflective=reflective

    def intersect_ray(self, ray_vector: Vector, origin=Vector.ZERO()):
        print(self.center, ray_vector)
        oc = origin - self.center

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

class Point():
    def __init__(self, x, y):
        self.x=x
        self.y=y

class Plane():
    def __init__(self, normal: Vector, distance):
        self.normal=normal
        self.distance=distance


class Vertex():
    def __init__(self, x, y, z):
        self.x=x
        self.y=y
        self.z=z

    def __add__(self, vertex2):
        return Vertex(self.x+vertex2.x, self.y+vertex2.y, self.z+vertex2.z)
    
    def __sub__(self, vertex2):
        return Vertex(self.x - vertex2.x, self.y - vertex2.y, self.z - vertex2.z)
    
    def multiply(self, n):
        return Vertex(self.x*n, self.y*n, self.z*n)
    
    def dot(self, vertex2):
        return self.x*vertex2.x + self.y*vertex2.y + self.z*vertex2.z
    
    def cross(self, other):
        return Vertex(
            (self.y * other.z) - (self.z * other.y),
            (self.z * other.x) - (self.x * other.z),
            (self.x * other.y) - (self.y * other.x)
        )
    

class Vertex4():
    def __init__(self, x,y,z,w):
        self.x=x
        self.y=y
        self.z=z
        self.w=w

    def __sub__(self, vertex2):
        return Vertex4(self.x - vertex2.x, self.y - vertex2.y, self.z - vertex2.z, self.w - vertex2.w)
    
    def cross(self, other):
        return Vertex4(
            (self.y * other.z) - (self.z * other.y),
            (self.z * other.x) - (self.x * other.z),
            (self.x * other.y) - (self.y * other.x),
            self.w
        )

class Matrix4x4:
    def __init__(self, data=None):
        if data is None:
            self.data = [[0.0 for _ in range(4)] for _ in range(4)]
        else:
            if len(data) != 4 or any(len(row) != 4 for row in data):
                raise ValueError("Matrix must be 4x4")
            self.data = [[float(val) for val in row] for row in data]

    def __repr__(self):
        return "\n".join([" ".join(f"{val:8.3f}" for val in row) for row in self.data])

    def __add__(self, other):
        return Matrix4x4([
            [self.data[i][j] + other.data[i][j] for j in range(4)]
            for i in range(4)
        ])

    def __sub__(self, other):
        return Matrix4x4([
            [self.data[i][j] - other.data[i][j] for j in range(4)]
            for i in range(4)
        ])

    def __mul__(self, other):
        if isinstance(other, Matrix4x4):
            result = [[0.0 for _ in range(4)] for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    for k in range(4):
                        result[i][j] += self.data[i][k] * other.data[k][j]
            return Matrix4x4(result)
        
        elif isinstance(other, Vertex4):
            result_array = [0,0,0,0]
            vertex=[other.x, other.y, other.z, other.w]
            for i in range(0,4):
                for j in range(0,4):
                    result_array[i]+=self.data[i][j]*vertex[j]
            return Vertex4(result_array[0], result_array[1],result_array[2],result_array[3])

        
        elif isinstance(other, (int, float)):
            return Matrix4x4([
                [self.data[i][j] * other for j in range(4)]
                for i in range(4)
            ])
        else:
            raise TypeError("Unsupported multiplication")

    def transpose(self):
        return Matrix4x4([
            [self.data[j][i] for j in range(4)]
            for i in range(4)
        ])

    def get(self, i, j):
        return self.data[i][j]

    def set(self, i, j, value):
        self.data[i][j] = float(value)

    def to_list(self):
        return [row[:] for row in self.data]
    

Identity4x4=Matrix4x4([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

def make_translation_matrix(translation:Vector):
    return Matrix4x4([[1, 0, 0, translation.x],
                 [0, 1, 0, translation.y],
                 [0, 0, 1, translation.z],
                 [0, 0, 0,             1]])

def make_scaling_matrix(scale):
    return Matrix4x4([[scale, 0, 0, 0],
                 [0, scale, 0, 0],
                 [0, 0, scale, 0],
                 [0, 0, 0, 1]])

def make_rot_matrix_y(degrees):
  cos = math.cos(degrees*math.pi/180.0)
  sin = math.sin(degrees*math.pi/180.0)

  return Matrix4x4([[cos, 0, -sin, 0],
                 [  0, 1,    0, 0],
                 [sin, 0,  cos, 0],
                 [  0, 0,    0, 1]])

class Triangle():
    def __init__(self, v1:Vertex, v2:Vertex, v3:Vertex, color:Color):
        self.v1=v1
        self.v2=v2
        self.v3=v3
        self.color=color

    def compute_normal(self):
        v1v2=self.v2-self.v1
        v1v3=self.v3-self.v1
        return v1v2.cross(v1v3)
        
class Model():
    def __init__(self, vertices, triangles, bounds_center, bounds_radius):
        self.triangles=triangles
        self.vertices=vertices
        self.bounds_center = bounds_center
        self.bounds_radius = bounds_radius

class Instance():
    def __init__(self, model:Model, position:Vector, orientation:Matrix4x4=Identity4x4, scale=1.0):
        self.model = model
        self.position = position
        self.orientation = orientation
        self.scale=scale
        self.transform = make_translation_matrix(self.position)*(self.orientation*make_scaling_matrix(scale))

class Camera():
    def __init__(self, position:Vector, orientation:Matrix4x4, planes:list[Plane]):
        self.position=position
        self.orientation = orientation
        self.clipping_planes = planes


