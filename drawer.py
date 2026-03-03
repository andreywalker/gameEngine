import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from PixelCanvasRaytracer import PixelCanvas
from PixelCanvasRaster import PixelCanvasRaster
from circles import Sphere, Vector, Color, Light,Point


SIZE = 800

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.Assignment1")
        GLib.set_application_name("Assignment1")


    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="Assignment1")
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

        canvas.draw_line(Point(300, 300),Point(270, 30), Color(20,200,180))

        canvas.draw_triangle(Point(-200, -250),Point(200, 50),Point(20, 250),Color(180,200,150))

        window.set_child(canvas)
        window.present()


# Create and run the application
if __name__ == "__main__":
    app = MyApplication()
    app.run()