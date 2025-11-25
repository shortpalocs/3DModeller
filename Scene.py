import sys
from sys import *
import numpy as np

from Node import Sphere, Cube, SnowFigure


class Scene(object):
    # the default depth from the camera to place an object at when using callback
    PLACE_DEPTH = 15.0




    def __init__(self):
        # The scene keeps a list of nodes [shapes] that are displayed
        self.node_list = list()
        # Keep track of currently selected node
        # Actions may depend or alter on whether a node is selected
        self.selected_node = None

    def add_node(self, node):
        # add new node to the scene
        self.node_list.append(node)


    def render(self):
        # render the scene, this function just calls the render function for each node
        for node in self.node_list:
            node.render()


    def pick(self, start, direction, mat):
        """
                Execute selection.

                start, direction describe a Ray.
                mat is the inverse of the current modelview matrix for the scene.
                """
        if self.selected_node is not None:
            self.selected_node.select(False)
            self.selected_node = None

        # Keep track of the closest hit.

        mindist = sys.maxsize # min distance
        closest_node = None
        for node in self.node_list:
            hit, distance = node.pick(start, direction, mat)
            if hit and distance < mindist:
                mindist, closest_node = distance, node

        # If we do hit something, keep track of that node

        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist
            closest_node.selected_loc = start + direction * mindist
            self.selected_node = closest_node


    def move_selected(self, start, direction, inv_modelview):
        """
                Move the selected node, if there is one.

                Consume:
                start, direction describes the Ray to move to
                mat is the modelview matrix for the scene
                """
        if self.selected_node is None: return


        # find the current depth and location of selected node
        node = self.selected_node
        depth = node.depth
        oldloc = node.selected_loc

        # the new location of te node is th same depth along the new ray
        newloc = (start + direction * depth)

        # transform the translation with the modelview matrix
        translation = newloc - oldloc
        pre_tran = np.array([translation[0], translation[1], translation[2], 0])
        translation = inv_modelview.dot(pre_tran)


        # translate the node and track its location

        node.translate(translation[0], translation[1], translation[2])
        node.selected_loc = newloc




    def place(self, shape, start, direction, inv_modelview):
        # place a new node


        new_node = None
        if shape == 'sphere': new_node = Sphere()
        if shape == 'cube': new_node = Cube()
        if shape == 'figure': new_node = SnowFigure()

        self.add_node(new_node)

        # place the node at the cursor in camera-space
        translation = (start + direction * self.PLACE_DEPTH)

        # convert translation to world-space

        pre_tran = np.array([translation[0], translation[1], translation[2], 1])
        translation = inv_modelview.dot(pre_tran)


        new_node.translate(translation[0], translation[1], translation[2])





    def rotate_selected_color(self, forwards):
        # rotate the color of the currently selected node (shape)
        if self.selected_node is None: return
        self.selected_node.rotate_color(forwards)

    def scale_selected(self, up):
        # scale the currently selected Node
        if self.selected_node is None: return
        self.selected_node.scale(up)


        # Keep track of closest hit
        mindist = sys.maxint
        closest_node = None
        for node in self.node_list:
            hit, distance = node.pick(start, direction, mat)
            if hit and distance < mindist:
                mindist, closest_node = distance, node


        # If we hit something, keep track of it

        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist
            closest_node.selected_loc = start + direction * mindist
            self.selected_node = closest_node