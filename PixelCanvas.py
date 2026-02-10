import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
import cairo
from circles import Vector, Circle, Color

class PixelCanvas(Gtk.DrawingArea):
    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.set_content_width(WIDTH)
        self.set_content_height(HEIGHT)
        self.WIDTH=WIDTH
        self.HEIGHT=HEIGHT
        self.MIN_DISTANCE = 0.1
        self.MAX_DISTANCE = 100000
        self.background = Color(255, 255, 255)
        self.viewport_size = 1
        self.projection_plane_z = 1
        self.spheres: list[Circle] = []

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
        y=self.WIDTH-y-1
        i = (y * self.WIDTH + x) * 4
        self.pixels[i + 0] = color.b
        self.pixels[i + 1] = color.g
        self.pixels[i + 2] = color.r
        self.pixels[i + 3] = 255

    def get_viewport_coordinates(self, x, y):
        return Vector(
            x * self.viewport_size / self.WIDTH,
            y * self.viewport_size / self.HEIGHT,
            self.projection_plane_z)
    
    def add_sphere(self, sphere: Circle):
        self.spheres.append(sphere)
    
    def trace_ray(self, ray):
        closest_intersection = 99999999999999
        closest_sphere = None
        for sphere in self.spheres:
            sphere_intersection = sphere.intersect_ray(ray)
            if sphere_intersection is None:
                continue
            elif sphere_intersection < closest_intersection and sphere_intersection > self.MIN_DISTANCE and sphere_intersection < self.MAX_DISTANCE:
                closest_intersection = sphere_intersection
                closest_sphere = sphere
        if closest_sphere is None:
            print("nospherer")
            return self.background
        return closest_sphere.color