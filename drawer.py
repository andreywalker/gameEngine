import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from PixelCanvasRaytracer import PixelCanvas
from PixelCanvasRaster import PixelCanvasRaster
from circles import Sphere, Vector, Color, Light,Point, Vertex, Plane, Triangle, Model, Camera, make_rot_matrix_y, Instance, Identity4x4
import math


SIZE = 1200

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.ass123")
        GLib.set_application_name("ass123")


    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="ass123")
        window.set_default_size(SIZE, SIZE)
        canvas = PixelCanvasRaster(SIZE, SIZE)
        '''
        canvas.add_sphere(Sphere(Vector(0, -1, 3), 1 , Color(255,0,0), 500, 0.2))
        canvas.add_sphere(Sphere(Vector(-2, 0, 4), 1 , Color(0,255,200), 10, 0.4))
        canvas.add_sphere(Sphere(Vector(2, 0, 4), 1 , Color(0,0,250), 500, 0.3))
        canvas.add_sphere(Sphere(Vector(0, -5001, 0), 5000 , Color(250,250,100),1000, 0.5))
        canvas.add_light(Light(1, 0.3))
        canvas.add_light(Light(2, 0.6, Vector(2, 1, 0)))
        canvas.add_light(Light(3, 0.2, Vector(1, 4, 4)))
        camera_position = Vector(3, 0, 1)
        camera_rotation_matrix = canvas.rotation_matrix(0, -60, 0)
        for x in range(int(-canvas.WIDTH/2), int(canvas.WIDTH/2)):
            for y in range(int(-canvas.HEIGHT/2), int(canvas.HEIGHT/2)):
                direction:Vector = canvas.get_viewport_coordinates(x, y)
                direction=direction.apply_matrix(camera_rotation_matrix)
                color:Color = canvas.trace_ray(direction, origin=camera_position)
                canvas.set_pixel(x,y,color)
                print(x,y,color)'''

        red = Color(255,20,50)
        green = Color(20, 255, 40)
        blue = Color(20, 30, 255)
        yellow = Color(240, 235, 50)
        purple = Color(255, 20, 240)
        cyan = Color(0, 255, 255)

        vertices = [
            Vertex(1, 1, 1),
            Vertex(-1, 1, 1),
            Vertex(-1, -1, 1),
            Vertex(1, -1, 1),
            Vertex(1, 1, -1),
            Vertex(-1, 1, -1),
            Vertex(-1, -1, -1),
            Vertex(1, -1, -1)]
        
        triangles = [
            Triangle(0, 1, 2, red),
            Triangle(0, 2, 3, red),
            Triangle(4, 0, 3, green),
            Triangle(4, 3, 7, green),
            Triangle(5, 4, 7, blue),
            Triangle(5, 7, 6, blue),
            Triangle(1, 5, 6, yellow),
            Triangle(1, 6, 2, yellow),
            Triangle(4, 5, 1, purple),
            Triangle(4, 1, 0, purple),
            Triangle(2, 6, 7, cyan),
            Triangle(2, 7, 3, cyan)
        ]

        cube = Model(vertices, triangles, Vertex(0, 0, 0), math.sqrt(3))
        
        s2 = 1.0 / math.sqrt(2)
        clipping_planes = {
            Plane(Vertex(  0,   0,  1), -1), 
            Plane(Vertex( s2,   0, s2),  0), 
            Plane(Vertex(-s2,   0, s2),  0), 
            Plane(Vertex(  0, -s2, s2),  0), 
            Plane(Vertex(  0,  s2, s2),  0), 
        }
        camera = Camera(Vector(0, 1, 0), make_rot_matrix_y(30), clipping_planes)

        instances=[
            Instance(cube, Vertex(-1.5,0 , 7), Identity4x4, 0.5),
            Instance(cube, Vertex(1.25, 2.5, 7.5), make_rot_matrix_y(195))
        ]
        canvas.render_scene(camera, instances)
        window.set_child(canvas)
        window.present()


# Create and run the application
if __name__ == "__main__":
    app = MyApplication()
    app.run()