from collections import defaultdict
from OpenGL.GLUT import glutGet, glutKeyboardFunc, glutMotionFunc, glutMouseFunc, \
    glutPostRedisplay, glutSpecialFunc
from OpenGL.GLUT import GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH, GLUT_DOWN, \
    GLUT_KEY_UP, GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT
import trackball

GLUT_LEFT_BUTTON = 0
GLUT_MIDDLE_BUTTON = 1
GLUT_RIGHT_BUTTON = 2



GLUT_LEFT_BUTTON = 0
GLUT_MIDDLE_BUTTON = 1
GLUT_RIGHT_BUTTON = 2
class Interaction(object):

    def __init__(self):
        """ Handles user interaction """
        # currently pressed mouse button
        self.pressed = None
        # the current location of the camera
        self.translation = [0, 0, 0, 0]
        # the trackball to calculate rotation
        self.trackball = trackball.Trackball(theta=-25, distance=15)
        # the current mouse location
        self.mouse_loc = None
        # Unsophisticated callback mechanism
        self.callbacks = defaultdict(list)

        self.register()

    def register(self):
        """ register callbacks with glut """
        print("Registering callbacks...")  # DEBUG
        glutMouseFunc(self.handle_mouse_button)
        print("Mouse func registered")  # DEBUG
        glutMotionFunc(self.handle_mouse_move)
        print("Motion func registered")  # DEBUG
        glutKeyboardFunc(self.handle_keystroke)
        print("Keyboard func registered")  # DEBUG
        glutSpecialFunc(self.handle_keystroke)
        print("Special func registered")  # DEBUG







        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_move)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)

    def register_callback(self, name, func):
        """ registers a callback for a certain event """
        self.callbacks[name].append(func)

    def trigger(self, name, *args, **kwargs):
        """ calls a callback, forwards the args """
        for func in self.callbacks[name]:
            func(*args, **kwargs)

    def translate(self, x, y, z):
        """ translate the camera """
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z

    def handle_mouse_button(self, button, mode, x, y):
        print(f"Mouse clicked: button={button}, mode={mode}, x={x}, y={y}")  # DEBUG
        """ Called when the mouse button is pressed or released """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - y  # invert the y coordinate because OpenGL is inverted
        self.mouse_loc = (x, y)

        if mode == GLUT_DOWN:
            print(f"Mode is GLUT_DOWN, button is {button}, GLUT_LEFT_BUTTON={GLUT_LEFT_BUTTON}")  # DEBUG
            self.pressed = button
            if button == GLUT_RIGHT_BUTTON:
                pass
            elif button == GLUT_LEFT_BUTTON:  # pick
                print("Triggering pick!")  # DEBUG
                self.trigger('pick', x, y)
            elif button == 3:  # scroll up
                self.translate(0, 0, 1.0)
            elif button == 4:  # scroll down
                self.translate(0, 0, -1.0)
        else:  # mouse button release
            self.pressed = None
        glutPostRedisplay()

    def handle_mouse_move(self, x, screen_y):
        """ Called when the mouse is moved """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - screen_y  # invert the y coordinate because OpenGL is inverted
        if self.pressed is not None:
            dx = x - self.mouse_loc[0]
            dy = y - self.mouse_loc[1]
            if self.pressed == GLUT_RIGHT_BUTTON and self.trackball is not None:
                # ignore the updated camera loc because we want to always rotate around the origin
                self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
            elif self.pressed == GLUT_LEFT_BUTTON:
                self.trigger('move', x, y)
            elif self.pressed == GLUT_MIDDLE_BUTTON:
                self.translate(dx / 60.0, dy / 60.0, 0)
            else:
                pass
            glutPostRedisplay()
        self.mouse_loc = (x, y)

    def handle_keystroke(self, key, x, screen_y):
        """ Called on keyboard input from the user """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - screen_y
        if key == 's':
            print("Sphere")
            self.trigger('place', 'sphere', x, y)
        elif key == 'c':
            print("Cube")
            self.trigger('place', 'cube', x, y)
        elif key == 'f':
            self.trigger('place', 'figure', x, y)
        elif key == GLUT_KEY_UP:
            self.trigger('scale', up=True)
        elif key == GLUT_KEY_DOWN:
            self.trigger('scale', up=False)
        elif key == GLUT_KEY_LEFT:
            self.trigger('rotate_color', forward=True)
        elif key == GLUT_KEY_RIGHT:
            self.trigger('rotate_color', forward=False)
        glutPostRedisplay()