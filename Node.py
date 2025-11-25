
import numpy as np
import random
import color
from transformation import *
from aabb import AABB
from OpenGL.raw.GL.VERSION.GL_1_0 import glPushMatrix, glMultMatrixf, glColor3f, glMaterialfv, GL_FRONT, GL_EMISSION, \
    glPopMatrix, glCallList

from primitive import G_OBJ_SPHERE, G_OBJ_CUBE


class Color:
    MIN_COLOR = 0
    MAX_COLOR = 255
    COLORS = [
        (1.0, 0.0, 0.0),  # red
        (0.0, 1.0, 0.0),  # green
        (0.0, 0.0, 1.0),  # blue
    ]








class Node(object):
    def __init__(self):
        self.color_index = random.randint(0, len(Color.COLORS)-1)
        self.aabb = AABB([0.0, 0.0, 0.0], [0.5, 0.5, 0.5])
        self.translation_matrix = np.identity(4)
        self.scaling_matrix = np.identity(4)
        self.selected = False

    def render(self):
        glPushMatrix()
        glMultMatrixf(np.transpose(self.translation_matrix).astype(np.float32).flatten())

        glMultMatrixf(self.scaling_matrix.astype(np.float32))
        cur_color = Color.COLORS[self.color_index]  # <-- use Color
        glColor3f(*cur_color)
        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])
        self.render_self()
        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        glPopMatrix()

    def pick(self, start, direction, mat):
        print(f"  Node {self.__class__.__name__} testing pick")  # DEBUG
        print(f"    AABB center: {self.aabb.center}, size: {self.aabb.size}")  # DEBUG

        newmat = np.dot(
            np.dot(mat, self.translation_matrix),
            np.linalg.inv(self.scaling_matrix)
        )

        results = self.aabb.ray_hit(start, direction, newmat)
        print(f"    Hit result: {results}")  # DEBUG
        return results
















    def select(self, select=None):
        # Toggles or sets selected state for that Node
        if select is not None:
            self.selected = select
        else:
            self.selected = not self.selected




    def rotate_color(self, forwards):
        self.color_index += 1 if forwards else -1
        if self.color_index > color.MAX_COLOR:
            self.color_index = color.MIN_COLOR
        if self.color_index < color.MIN_COLOR:
            self.color_index = color.MAX_COLOR


    def scale(self, up):
        s = 1.1 if up else 0.9
        self.scaling_matrix = np.dot(self.scaling_matrix, [s,s,s])

    def scaling(scale):
        s = np.identity(4)
        s[0,0] = scale[0]
        s[1,1] = scale[1]
        s[2,2] = scale[2]
        s[3,3] = 1
        return s



    def translate(self, x, y, z):
        self.translation_matrix = np.dot(self.translation_matrix, translation([x, y, z]))




    def render_self(self):
        raise NotImplementedError(
            "Abstract node class doesn't define 'render_self"
        )


class Primitive(Node):
    def __init__(self):
        super(Primitive, self).__init__()
        self.call_list = None


    def render_self(self):
        glCallList(self.call_list)


# ~3 Hour mark

class Sphere(Primitive): # Inheritance from Primitive class
    """"Sphere Primitive!"""
    def __init__(self):
        super(Sphere, self).__init__()
        self.call_list = G_OBJ_SPHERE

class Cube(Primitive): # Inheritance from Primitive
    def __init__(self):
        super(Cube, self).__init__()
        self.call_list = G_OBJ_CUBE


class HierarchialNode(Node):
    def __init__(self):
        super(HierarchialNode, self).__init__()
        self.child_nodes = []

    def render_self(self):
        for child in self.child_nodes:
            child.render()


# Make the snowfigure object


class SnowFigure(HierarchialNode):
    def __init__(self):
        super(SnowFigure, self).__init__()
        self.child_nodes = [Sphere(), Sphere(), Sphere()]
        self.child_nodes[0].translate(0, -0.6, 0) # scale 1.0
        self.child_nodes[1].translate(0, 0.1, 0)
        self.child_nodes[1].scaling_matrix = np.dot(
            self.scaling_matrix, ([0.8, 0.8, 0.8]))

        self.child_nodes[2].translate(0, 0.75, 0)
        self.child_nodes[2].scaling_matrix = np.dot(
            self.scaling_matrix, ([0.7, 0.7, 0.7]))


        for child_node in self.child_nodes:
            child_node.color_index = Color.color.MIN_COLOR






















    def pick(self, start, direction, mat):
        """ Return whether or not the ray hits the object
                  Consume:  start, direction    the ray to check
                            mat                 the modelview matrix to transform the ray by """

        # transform the modelview matrix by  the current translation
        newmat = np.dot(np.dot(mat, self.translation_matrix), np.linalg.inv(self.scaling_matrix))
        results = self.aabb.ray_hit(start, direction, newmat)
        return results
    def select(self, select=None):
        if select is not None:
            self.selected = select
        else:
            self.selected = not self.selected







