import sys

from numpy.linalg import norm, inv
from OpenGL.GL import glGetFloatv
from Interaction import Interaction
from Node import Sphere, HierarchialNode, Cube
from Scene import *
from OpenGL.GL import GL_PROJECTION_MATRIX, GL_VIEWPORT, glGetIntegerv
import OpenGL
import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glEnable, GL_LIGHT0, glCullFace, GL_BACK, GL_DEPTH_TEST, glDepthFunc, GL_LESS, \
    GL_CULL_FACE, GL_POSITION, glLightfv, GL_SPOT_DIRECTION, GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, glColorMaterial, \
    GL_COLOR_MATERIAL, GL_LIGHTING, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glLoadIdentity, glTranslated, \
    GL_MODELVIEW_MATRIX, glDisable, glCallList, GL_OBJECT_PLANE, glPopMatrix, GL_PROJECTION, glViewport
from OpenGL.raw.GLES1.VERSION.GLES1_1_0 import glClearColorx, glClear, glMatrixMode, glPushMatrix, glMultMatrixf
from OpenGL.raw.GLES2.VERSION.GLES2_2_0 import GL_COLOR_BUFFER_BIT, glFlush, glClearColor
from OpenGL.raw.GLU import gluPerspective
from OpenGL.GLUT import glutInit, glutInitWindowSize, glutCreateWindow, glutInitDisplayMode, GLUT_SINGLE, GLUT_RGB, \
    glutDisplayFunc, glutMainLoop, glutGet, GLUT_WINDOW_WIDTH, GLUT_WINDOW_HEIGHT

from OpenGL.GLU import gluUnProject

from OpenGL import *

from primitive import init_primitives


class Viewer(object):
    def __init__(self):
        self.init_interface()
        self.init_opengl()
        self.init_scene()
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # MOVE THIS BEFORE glutInitWindowSize
        glutInitWindowSize(640, 480)
        glutCreateWindow("3d moddellerlerl")
        glutDisplayFunc(self.render)


    def init_opengl(self):
        # init the opengl settings to actually render the scene
        self.inverseModelView = np.identity(4)
        self.modelView = np.identity(4)


        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION,(0, 0, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, (0,0,-1))

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)


        self.grid_list = self.make_grid()


    def make_grid(self):
        from OpenGL.GL import glGenLists, glNewList, GL_COMPILE, glBegin, GL_LINES, glVertex3f, glEnd, glEndList, glColor3f
        grid_list = glGenLists(1)
        glNewList(grid_list, GL_COMPILE)

        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)


        for i in range(-10, 11): # edit this later
            glVertex3f(i, 0, -10)
            glVertex3f(i, 0, 10)
            # Lines parallel to z axis
            glVertex3f(-10, 0, i)
            glVertex3f(10, 0, i)


        glEnd()
        glEndList()

        return grid_list


    def init_scene(self):
        # init scene
        # Make Scene later in Scene file!
        self.scene = Scene()
        self.create_sample_scene()

    def create_sample_scene(self):
        cube_node = Cube() # Work on this later!
        cube_node.translate(2, 0, 2)
        cube_node.color_index = 0
        self.scene.add_node(cube_node)

        sphere_node = Sphere() # make sphere object later
        sphere_node.translate(-2, 0, 2)
        sphere_node.color_index = 1
        self.scene.add_node(sphere_node)

    def init_interaction(self):
        # Init user interaction and their callbacks
        self.interaction = Interaction() # work on this later
        self.interaction.register_callback('pick', self.pick)
        self.interaction.register_callback('move', self.move)
        self.interaction.register_callback('place', self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale', self.scale)


    def move(self, x, y):
        # execute a move command on the scene
        start, direction = self.get_ray(x, y)
        self.scene.move_selected(start, direction, self.inverseModelView)


    def rotate_color(self, forward):
        # rotate the color of the selected Node.
        # boolean 'forward' indicates direction of rotation
        self.scene.rotate_selected_color(forward)



    def place(self, shape, x, y):
        # execute a placement of a new primitive onto the scene
        start, direction = self.get_ray(x,y)




    def scale(self, up):
        # scale the selected node. boolean up indicates scaling larger
        self.scene.scale_selected(up)


    def render(self):
        # The render pass for the scene
        self.init_view()

        glEnable(GL_LIGHTING)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Load the modelview matrix from the current state of trackball
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        loc = self.interaction.translation
        glTranslated(loc[0], loc[1], loc[2])
        glMultMatrixf(self.interaction.trackball.matrix)


        # store the inverse of the currentviewModel

        currentModelView = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView = np.transpose(currentModelView)
        self.inverseModelView = inv(np.transpose(currentModelView)) # translate from one coordinate space to another

        # render the scene, this will call render function for each object

        self.scene.render()

        # draw grid
        glDisable(GL_LIGHTING)
        glCallList(self.grid_list) # modify this later, draws coordinate plane
        glPopMatrix()


        # flush the buffers so that the scene can actually be drawn
        glFlush()


    def init_view(self):
        # init projection matrix
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect_ratio = float(xSize) / float(ySize)

        # load projection matrix

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glViewport(0,0,xSize,ySize)
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        glTranslated(0,0,-15)

    def get_ray(self, x, y):
        # generate a ray beginning at the near plane, in the direction that x and y coord are facing
        # Use the current OpenGL state from the last render - don't reset matrices!

        # get two points on the line
        start = np.array(gluUnProject(x, y, 0.001))
        end = np.array(gluUnProject(x, y, 0.999))

        # convert these two points into a ray
        direction = end - start
        direction = direction / norm(direction)

        return (start, direction)

    def pick(self, x, y):
        print(f"Pick called! x={x}, y={y}")  # DEBUG
        # execute pick of an object, selects an object in the scene based off if ray made contact with any node
        start, direction = self.get_ray(x, y)
        print(f"Ray: start={start}, direction={direction}")  # DEBUG
        self.scene.pick(start, direction, self.modelView)








    def main_loop(self):
        glutMainLoop()

if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()







