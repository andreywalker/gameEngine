import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from PixelCanvas import PixelCanvas
from circles import Sphere, Vector, Color, Light


SIZE = 400

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.Assignment1")
        GLib.set_application_name("Assignment1")


    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="Assignment1")
        window.set_default_size(SIZE, SIZE)
        canvas = PixelCanvas(SIZE, SIZE)
        canvas.add_sphere(Sphere(Vector(0, -1, 3), 1 , Color(180,50,0), 10))
        canvas.add_sphere(Sphere(Vector(-2, 0, 4), 1 , Color(0,200,200), 200))
        canvas.add_sphere(Sphere(Vector(2, 0, 4), 1 , Color(50,50,200), 100))
        canvas.add_sphere(Sphere(Vector(0, -5001, 0), 5000 , Color(100,100,100),10))
        canvas.add_light(Light(1, 0.15))
        canvas.add_light(Light(2, 0.6, Vector(2, 1, 0)))
        canvas.add_light(Light(3, 0.2, Vector(1, 4, 4)))


        for x in range(int(-canvas.WIDTH/2), int(canvas.WIDTH/2)):
            for y in range(int(-canvas.HEIGHT/2), int(canvas.HEIGHT/2)):
                direction:Vector = canvas.get_viewport_coordinates(x, y)
                color:Color = canvas.trace_ray(direction)
                canvas.set_pixel(x,y,color)
                print(x,y,color)
        window.set_child(canvas)
        window.present()


# Create and run the application
if __name__ == "__main__":
    app = MyApplication()
    app.run()