import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
from PixelCanvas import PixelCanvas
from circles import Circle, Vector, Color


size = 400

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.Assignment1")
        GLib.set_application_name("Assignment1")


    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="Assignment1")
        window.set_default_size(size, size)
        canvas = PixelCanvas(size, size)
        canvas.add_sphere(Circle(Vector(0, -1, 3), 1 , Color(255,0,0)))
        canvas.add_sphere(Circle(Vector(-2, 0, 4), 1 , Color(0,255,0)))
        canvas.add_sphere(Circle(Vector(2, 0, 4), 1 , Color(0,0,255)))
        canvas.add_sphere(Circle(Vector(0, -5001, 0), 5000 , Color(100,100,100)))

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