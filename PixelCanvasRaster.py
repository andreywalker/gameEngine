import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
import cairo
import math
from circles import Vector, Sphere, Color, Light, Point

class PixelCanvasRaster(Gtk.DrawingArea):
    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.set_content_width(WIDTH)
        self.set_content_height(HEIGHT)
        self.WIDTH=WIDTH
        self.HEIGHT=HEIGHT
        self.background = Color(0, 0, 0)
        self.viewport_size = 1
        self.viewport_distance = 1
        self.points:list[Point]=[]


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
        x = int(x)
        y = int(y)
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
    
    def add_point(self, p:Point):
        self.points.append(p)

    def interpolate(self,i0, d0, i1, d1):
        if i0 == i1:
            return list(d0)

        values = list()
        a = (d1 - d0) / (i1 - i0)
        d = d0
        for i in range(i0, i1):
            values.append(d)
            d += a
        return values


    def draw_line(self, p1: Point, p2:Point, color:Color):
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        if abs(dx) > abs(dy):
            # The line is horizontal-ish. Make sure it's left to right.
            if dx < 0:
                swap:Point = p1
                p1 = p2 
                p2 = swap
            # Compute the Y values and draw.
            
            y_array = self.interpolate(p1.x, p1.y, p2.x, p2.y)
            for x in range(int(p1.x), int(p2.x)):
                self.set_pixel(x, y_array[int(x - p1.x)], color)
            
        else:
            #The line is verical-ish. Make sure it's bottom to top.
            if dy < 0:
                swap:Point = p1 
                p1 = p2
                p2 = swap

            # Compute the X values and draw.
            x_array = self.interpolate(p1.y, p1.x, p2.y, p2.x)
            for y in range(p1.y, p2.y):
                self.set_pixel(int(x_array[y - p1.y]), int(y), color)
    
    def draw_triangle(self, p1:Point, p2:Point, p3:Point, color:Color):
        # Sort the points from bottom to top.
        if p2.y < p1.y:
            swap = p1
            p1 = p2
            p2 = swap
        if p3.y < p1.y:
            swap = p1
            p1 = p3
            p3 = swap

        if p3.y < p2.y:
            swap = p2
            p2 = p3
            p3 = swap

        # Compute X coordinates of the edges.
        x12 = self.interpolate(p1.y, p1.x, p2.y, p2.x)
        x23 = self.interpolate(p2.y, p2.x, p3.y, p3.x)
        x13 = self.interpolate(p1.y, p1.x, p3.y, p3.x)

        # Merge the two short sides.

        x123 = x12+x23
        m = len(x13) // 2

        if x13[m] < x123[m]:
            x_left = x13
            x_right = x123
        else:
            x_left = x123
            x_right = x13

        # Draw horizontal segments.
        print("------------------------------------------------------------------------------------------")
        print(len(x_left))
        print()
        print(len(x_right))
        for i in range(len(x_left)):
            y = p1.y + i

            xl = int(x_left[i])
            xr = int(x_right[i])

            for x in range(xl, xr):
                self.set_pixel(x, y, color)
