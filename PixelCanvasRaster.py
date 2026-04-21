import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib
import cairo
import math
from circles import Vector, Sphere, Color, Light, Point, Plane, Vertex, Vertex4, Matrix4x4, Identity4x4, Instance, Camera, Model, Triangle, make_scaling_matrix, make_translation_matrix

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
        self.depth_buffer = [None] * (WIDTH * HEIGHT)
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
        i0,d0,i1,d1=int(i0),int(d0), int(i1), int(d1)
        if i0 == i1:
            return [d0]

        values = list()
        a = (d1 - d0) / (i1 - i0)
        d = d0
        for i in range(i0, i1+1):
            values.append(d)
            d += a
        return values
    
    def edge_interpolate(self, y0, v0, y1, v1, y2, v2):
        v01 = self.interpolate(y0, v0, y1, v1)
        v12 = self.interpolate(y1, v1, y2, v2)
        v02 = self.interpolate(y0, v0, y2, v2)

        # Concatenate short sides, removing the duplicate middle point
        v01.pop()
        v012 = v01 + v12
        return v02, v012


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
                self.set_pixel(int(x), int(y_array[int(x - p1.x)]), color)
            
        else:
            #The line is verical-ish. Make sure it's bottom to top.
            if dy < 0:
                swap:Point = p1 
                p1 = p2
                p2 = swap

            # Compute the X values and draw.
            x_array = self.interpolate(p1.y, p1.x, p2.y, p2.x)
            for y in range(int(p1.y), int(p2.y+1)):
                self.set_pixel(int(x_array[int(y - p1.y)]), int(y), color)
    
    def draw_frame_triangle(self, p1:Point, p2:Point, p3:Point, color:Color):
        self.draw_line(p1, p2, color)
        self.draw_line(p2, p3, color)
        self.draw_line(p3, p1, color)

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
        x12.pop()
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

    def viewport_to_canvas(self, p:Point):
        return Point(p.x*self.WIDTH/self.viewport_size, p.y*self.HEIGHT/self.viewport_size)
    
    def project_vertex(self, v:Vertex):
        return self.viewport_to_canvas(Point(v.x*self.viewport_distance/v.z, v.y*self.viewport_distance/v.z))
    
    def render_triangle(self, t:Triangle, projected):
        self.draw_frame_triangle(
            projected[t.v1],
            projected[t.v2],
            projected[t.v3],
            t.color)
        
    def render_triangle(self, triangle:Triangle, vertices, projected, backface_culling=True):
        # 1. Sort vertex indexes by projected Y coordinate
        # triangle.v1, v2, v3 are the indices into the vertex/projected lists
        idxs = [triangle.v1, triangle.v2, triangle.v3]
        idxs.sort(key=lambda i: projected[i].y)
        i0, i1, i2 = idxs

        v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
        p0, p1, p2 = projected[i0], projected[i1], projected[i2]

        # 2. Compute Normal and Backface Culling
        # Use original triangle indices to keep winding order consistent
        edge1 = vertices[triangle.v2] - vertices[triangle.v1]
        edge2 = vertices[triangle.v3] - vertices[triangle.v1]
        normal = edge1.cross(edge2)

        if backface_culling:
            # Vector from vertex to camera (camera is at 0,0,0 in view space)
            # Since camera is origin, camera - vertex is just -vertex
            vertex_to_camera = Vector(-v0.x, -v0.y, -v0.z)
            # If dot product <= 0, the triangle faces away
            if vertex_to_camera.dot(Vector(normal.x, normal.y, normal.z)) <= 0:
                return

        # 3. Interpolate X and 1/Z (inv_z) across the edges
        x02, x012 = self.edge_interpolate(p0.y, p0.x, p1.y, p1.x, p2.y, p2.x)
        iz02, iz012 = self.edge_interpolate(p0.y, 1.0/v0.z, p1.y, 1.0/v1.z, p2.y, 1.0/v2.z)

        # 4. Determine which side is left and which is right
        m = len(x02) // 2
        if m < len(x012) and x02[m] < x012[m]:
            x_left, x_right = x02, x012
            iz_left, iz_right = iz02, iz012
        else:
            x_left, x_right = x012, x02
            iz_left, iz_right = iz012, iz02

        # 5. Draw horizontal segments (Scanlines)
        for i in range(len(x_left)):
            y = int(p0.y) + i
            xl, xr = int(x_left[i]), int(x_right[i])
            zl, zr = iz_left[i], iz_right[i]
            
            # Interpolate 1/Z across the scanline
            z_scan = self.interpolate(xl, zl, xr, zr)

            for x in range(xl, xr + 1):
                # Calculate index in z_scan list
                z_idx = x - xl
                if z_idx < len(z_scan):
                    inv_z = z_scan[z_idx]
                    if self.update_depth_buffer_if_closer(x, y, inv_z):
                        self.set_pixel(x, y, triangle.color)

    def update_depth_buffer_if_closer(self, x, y, inv_z):
        # Convert canvas coordinates to buffer coordinates
        scr_x = (self.WIDTH // 2) + x
        scr_y = (self.HEIGHT // 2) - y - 1

        if 0 <= scr_x < self.WIDTH and 0 <= scr_y < self.HEIGHT:
            offset = int(scr_x + (self.WIDTH * scr_y))
            current_depth = self.depth_buffer[offset]
            
            # Higher inv_z means the point is closer to the camera
            if current_depth is None or inv_z > current_depth:
                self.depth_buffer[offset] = inv_z
                return True
        return False
    
    def clip_triangle(self, triangle:Triangle, plane:Plane, triangles:list[Triangle], vertices:list[Vertex]):
        v0 = vertices[triangle.v1]
        v1 = vertices[triangle.v2]
        v2 = vertices[triangle.v3]

        in0 = plane.normal.dot(v0) + plane.distance > 0
        in1 = plane.normal.dot(v1) + plane.distance > 0
        in2 = plane.normal.dot(v2) + plane.distance > 0

        in_count = in0 + in1 + in2
        if in_count == 3:
            triangles.append(triangle)
        return triangles

    def transform_clip(self,clipping_planes:list[Plane], model:Model, scale, transform:Matrix4x4):
        center = transform*Vertex4(model.bounds_center.x, model.bounds_center.y, model.bounds_center.z, 1)
        radius = model.bounds_radius*scale
        for p in clipping_planes:
            distance = p.normal.dot(center) + p.distance
            if distance < -radius:
                return None
        
        vertices = []
        for vertex in model.vertices:
            vertices.append(transform*Vertex4(vertex.x, vertex.y, vertex.z, 1))
        
        triangles = model.triangles[:]
        for p in clipping_planes:
            new_triangles = []
            for t in triangles:
                new_triangles = self.clip_triangle(t, p, new_triangles, vertices)
            triangles = new_triangles

        return Model(vertices, triangles, center, model.bounds_radius)
        


    
    def render_model(self, model: Model):
        projected = []

        for vertex in model.vertices:
            projected.append(self.project_vertex(vertex))

        for triangle in model.triangles:
            self.render_triangle(triangle, model.vertices, projected)

    def render_scene(self, camera: Camera, instances: list[Instance]):
        camera_matrix = make_translation_matrix(
            camera.position.multiply(-1)
        ) * camera.orientation.transpose()

        for instance in instances:
            transform = camera_matrix * instance.transform
            clipped = self.transform_clip(clipping_planes=camera.clipping_planes, model = instance.model, scale=instance.scale, transform=transform)
            if clipped:
                self.render_model(clipped)

    def update_depth_buffer_if_closer(self, x, y, inv_z):
        # (x | 0) in JS truncates to integer; in Python, we use int()
        # We use // for integer division to ensure the results are ints
        scr_x = (self.WIDTH // 2) + int(x)
        scr_y = (self.HEIGHT // 2) - int(y) - 1

        # Bounds check
        if scr_x < 0 or scr_x >= self.WIDTH or scr_y < 0 or scr_y >= self.HEIGHT:
            return False

        # Calculate 1D array index from 2D coordinates
        offset = scr_x + (self.WIDTH * scr_y)

        # depth_buffer[offset] == undefined logic:
        # In Python, we typically initialize the list with None or a very small number
        current_depth = self.depth_buffer[offset]
        
        if current_depth is None or current_depth < inv_z:
            self.depth_buffer[offset] = inv_z
            return True
            
        return False
    
    def clear_all(self):
        self.depth_buffer=[]