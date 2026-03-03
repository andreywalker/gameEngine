import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
import cairo
import math
from circles import Vector, Sphere, Color, Light

class PixelCanvas(Gtk.DrawingArea):
    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.set_content_width(WIDTH)
        self.set_content_height(HEIGHT)
        self.WIDTH=WIDTH
        self.HEIGHT=HEIGHT
        self.MIN_DISTANCE = 1
        self.MAX_DISTANCE = 100000
        self.background = Color(0, 0, 0)
        self.viewport_size = 1
        self.viewport_distance = 1
        self.spheres: list[Sphere] = []
        self.lights: list[Light] = []
        self.faraway = 99999999999999
        self.EPSILON =0.001

        # RGBA pixel buffer
        self.pixels = bytearray(WIDTH * HEIGHT * 4)

        self.set_draw_func(self.on_draw)

    def on_draw(self, area, cr, width, height):
        surface = cairo.ImageSurface.create_for_data(
            self.pixels,
            cairo.FORMAT_ARGB32,
            self.WIDTH,
            self.HEIGHT,
            self.WIDTH * 4,
        )

        cr.set_source_surface(surface, 0, 0)
        cr.paint()

    def set_pixel(self, x, y, color:Color):
        x+=int(self.WIDTH/2)
        y+=int(self.HEIGHT/2)
        y=self.HEIGHT-y-1
        i = (y * self.WIDTH + x) * 4
        self.pixels[i + 0] = int(color.b)
        self.pixels[i + 1] = int(color.g)
        self.pixels[i + 2] = int(color.r)
        self.pixels[i + 3] = 255

    def get_viewport_coordinates(self, x, y):
        return Vector(
            x * self.viewport_size / self.WIDTH,
            y * self.viewport_size / self.HEIGHT,
            self.viewport_distance)
    
    def rotation_matrix(self, ax, ay, az):
        ax = math.radians(ax)
        ay = math.radians(ay)
        az = math.radians(az)

        cx, sx = math.cos(ax), math.sin(ax)
        cy, sy = math.cos(ay), math.sin(ay)
        cz, sz = math.cos(az), math.sin(az)

        # R = Rz * Ry * Rx
        return [
            [cz*cy, cz*sy*sx - sz*cx, cz*sy*cx + sz*sx],
            [sz*cy, sz*sy*sx + cz*cx, sz*sy*cx - cz*sx],
            [-sy,   cy*sx,            cy*cx]
        ]


    def add_sphere(self, sphere: Sphere):
        self.spheres.append(sphere)
    
    def add_light(self, light: Light):
        self.lights.append(light)
    
    def reflect_ray(self, ray:Vector, normal:Vector):
        v = ray.multiply(-1)
        return normal.multiply(2*normal.dot(v)) - v

    def compute_lighting(self, intersection_point:Vector, normal:Vector, ray:Vector, specular):
        i = 0.0
        max_distance = self.MAX_DISTANCE
        for light in self.lights:
            #ambient
            if light.type == 1:
                i += light.intensity
                continue
            #point
            elif light.type == 2:
                raw:Vector =light.pos_dir - intersection_point
                surface_to_light=raw.normalize()
                max_distance=raw.length()
            #directional
            else:
                surface_to_light:Vector = light.pos_dir

            blocker, _ = self.closest_intersection(surface_to_light, origin=intersection_point, min_distance=self.EPSILON, max_distance=max_distance)
            if blocker is not None:
                continue
            
            n_dot_l = normal.dot(surface_to_light)
            if n_dot_l > 0:
                i += light.intensity * n_dot_l/(normal.length() * surface_to_light.length())
            if specular!=-1:
                reflected:Vector = normal.multiply(2.0*n_dot_l)-surface_to_light
                r_dot_v = reflected.dot(ray.multiply(-1))
                if r_dot_v>0:

                    i += light.intensity * math.pow(r_dot_v / (reflected.length() * ray.length()), specular)
        if i>1.0:
            i=1.0
        return i

    def closest_intersection(self, ray:Vector, origin=Vector.ZERO(),min_distance=0,max_distance=1.0 ):
        if min_distance==0:
            min_distance=self.MIN_DISTANCE
        if max_distance==1:
            max_distance=self.MAX_DISTANCE
        closest_intersection = self.faraway
        closest_sphere = None
        for sphere in self.spheres:
            sphere_intersection = sphere.intersect_ray(ray, origin)
            if sphere_intersection is None:
                continue
            elif sphere_intersection < closest_intersection and sphere_intersection > min_distance and sphere_intersection < max_distance:
                closest_intersection = sphere_intersection
                closest_sphere = sphere
        return closest_sphere, closest_intersection
    
    def trace_ray(self, ray:Vector, origin:Vector=Vector.ZERO(), min_distance=0, recursion_depth = 3):
        if min_distance==0:
            min_distance=self.MIN_DISTANCE
        closest_sphere, closest_intersection =self.closest_intersection(ray,min_distance=min_distance, origin=origin)
        if closest_sphere is None:
            print("nospherer")
            return self.background
        intersection_point:Vector = origin + ray.multiply(closest_intersection)
        normal:Vector = intersection_point-closest_sphere.center
        normal = normal.multiply(1.0/normal.length())
        local_color:Color = closest_sphere.color.multiply(self.compute_lighting(intersection_point, normal, ray, closest_sphere.specular))

        if recursion_depth<=0 or closest_sphere.reflective<=0:
            return local_color
        ray = self.reflect_ray(ray, normal).normalize()
        reflected_color:Color = self.trace_ray(ray, origin=intersection_point, min_distance=self.EPSILON, recursion_depth=recursion_depth-1)
        return local_color.mix(reflected_color, closest_sphere.reflective)
    
