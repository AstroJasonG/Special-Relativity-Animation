""" animate_shape.py
main animation script using SR_transforms and make_shape
@author: Jason
dependencies: See below
"""

import vispy
import vispy.scene
from make_shape import Make_shape
from SR_transforms import Transform
from vispy.scene import visuals
from vispy import app, gloo
from moviepy.editor import VideoClip
from vispy.gloo.util import _screenshot
import imageio
import numpy as np


def startup(fname, dimension, npoints, anim, dcamera, shift=[0, 0, 0], beta=0):
    """Initialization of animation parameters
        See visual_setup for initialization of visual parameters
    Input:
        Dimension: int [1,3]=rod/square/cube
        npoints: int [1,infty) number of points to build shape
        anim:
            anim = 0: Static images
            anim = 1: Animation
            anim = other: run visual without saving to file
        shift: (3,) Array/int translates shape
        dcamera: float, camera distance along y axis
    Returns:
        linepos: Initial points of N-dimensional rods
        linepos0: Static initial points used for transfromations
        linepos1: Initial points used for additional shapes
        *tid: Initialization of time variable used in Update() - do not change
        *beta: Initialization of beta - do not change
        dcamera: float, physical camera distance from origin
    """
    cube = Make_shape(dimension)
    verts = cube.verts()
    linepos = cube.frame(verts + shift, npoints)
    linepos0 = cube.frame(verts + shift, npoints)
    if dimension == 1:
        linepos1 = cube.frame(verts + [0, 0, 0.5], npoints)
    else:
        linepos1 = cube.frame(verts + shift, npoints)
    if anim == 0:
        beta = beta
    else:
        beta = 0
    tid = 0
    return(fname, dimension, npoints, anim, linepos, linepos0, linepos1, tid,
           beta, dcamera)


# Change inputs of this function to visual you want to produce
(fname, dimension, npoints, anim, linepos, linepos0, linepos1, tid, beta,
    dcamera) = startup(
         fname="PT_bold", dimension=1, npoints=50, anim=1, dcamera=1,
         shift=[0, 0, 0], beta=0)

# --------------------------Canvas setup-------------------------------------
""" Setup of Vispy canvas objects, see Vispy documentation for details
"""
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True, resizable=True,
                                 dpi=200, always_on_top=True, bgcolor="black")
view = canvas.central_widget.add_view()
# ---------------------------------------------------------------------------


def visualsetup(title, linespos=linepos, linepos0=linepos0, linepos1=linepos1,
                compare=False, LT=False):
    """ Initialization of line visuals (rods) to the Vispy Canvas.
    Input:
        title: str, title to appear at the top of animation
        default inputs:
            linepos, linepos0, linepos1
        compare: bool
            True: add static comparison shape
        LT: bool
            True: add Lorentz transformed shape (dimension 1, 2)
    Vispy LinePlot parameters:
        width: int, width of the line visual
        marker size: size of points in linepos (size=0 to hide)
        connect: line visual connection type
            strip: solid line
            segments: dashed line
        color: can be hex, or string
    """
    lines = np.empty(0,)
    lines0 = np.empty(0,)
    lines1 = np.empty(0,)
    for k in range(len(linepos)):
        result = np.array([visuals.LinePlot(linepos[k], width=4,
                                            marker_size=0, connect="strip")])
        result2 = np.array([visuals.LinePlot(
                linepos0[k], color='pink', width=2, marker_size=0,
                connect="segments")])
        result3 = np.array([visuals.LinePlot(
                linepos1[k], color='pink', width=2, marker_size=0,
                connect="segments")])
        lines = np.append(lines, result, axis=0)
        lines0 = np.append(lines0, result2, axis=0)
        lines1 = np.append(lines1, result3, axis=0)
    for j in range(len(lines)):
        view.add(lines[j])
        if compare:
            view.add(lines0[j])
        if LT and dimension in [1, 2]:
            view.add(lines1[j])

    axis = visuals.XYZAxis(parent=view.scene)
    titletext = visuals.Text(text=title, color="white", pos=(0, 0, -0.5),
                             font_size=30)
    view.add(titletext)

    if LT and dimension == 1 and anim in [1, 2]:
        """ Some labels for when comparing Lorentz to Penrose-Terrell
        """
        text1 = visuals.Text(text="Lorentz ", color="white",
                             pos=(-0.2, 0, 0.5), font_size=40)
        view.add(text1)
        text2 = visuals.Text(text="Loretnz + optical", color="white",
                             pos=(-0.4, 0, 0), font_size=40)
        view.add(text2)
    return lines, lines0, lines1, axis, compare, LT


lines, lines0, lines1, axis, compare, LT = visualsetup(
        "Penrose Terrell Rotation (1D)", compare=False, LT=False)


def update(ev):
    """ Global animation function that cyles beta from [0,1) then (1,0], while
    applying Lorentz transformations or Optical Distortion/Penrose-Terrell
    effects and updating rod point positions and sets all data to the Vispy
    canvas.

    Update is a Vispy specific function that behaves like a while loop which
    breaks on a timer.
    **Note: To avoid the singularity at beta=1, a small tolerance is set to
    decrease beta back to 0 after coming sufficiently close to 1
    Input:
        ev: Event sent to update by the Vispy canvas - in this case clock
        ticks
    Globals (need to be updated globally):
        linepos, beta: updated but the same as previous
        tid: int, clock tick counter
        iter_num: numer of iterations to run in the animation
    """
# -------------singularity handling and beta turn around----------------------
    global linepos, linepos0, linespos1, beta, tid, iter_num
    if anim != 0:
        if tid < np.around(((iter_num / 2) - 1), decimals=1):
            beta += 0.001
        elif tid > np.around((iter_num / 2), decimals=1):
            beta -= 0.001
    tid += 1
# ----------------------Transformation----------------------------------------
    T = Transform(beta)
    if dimension == 1:
        linepos[0][:, 0] = T.PT(linepos0, dcamera, 0)
        if LT:
            linepos1[0][:, 0] = linepos0[0][:, 0] / T.LT()[2]
    elif dimension == 2:
        for k in range(4):
            linepos[k][:, 0] = T.PT(linepos0, dcamera, k)
            if LT:
                linepos1[k][:, 0] = linepos0[k][:, 0] / T.LT()[2]
    elif dimension == 3:
        for k in range(len(lines)):
            linepos[k][:, 0] = T.PT(linepos0, dcamera, k)
# -------------------------setting data to lines------------------------------
    fcolor = '#04f2ff'
    bcolor = '#ff0479'
    for j in range(len(lines)):
        if dimension in [1, 2]:
            lines[j].set_data(linepos[j], marker_size=1, color=fcolor)
            if LT:
                lines1[j].set_data(linepos1[j], marker_size=1, color="pink")
        elif dimension == 3:
            lines[j].set_data(linepos[j], marker_size=1, color='grey')
            if j in [0, 4, 5, 6]:
                lines[j].set_data(linepos[j], marker_size=1, color=bcolor)
            elif j in [3, 7, 9, 11]:
                lines[j].set_data(linepos[j], marker_size=1, color=fcolor)


# -------------------------event timer----------------------------------------
""" Timer connected to update events
"""
total_time = 10
iter_num = 2000
interval_num = total_time / iter_num
timer = app.Timer()
timer.connect(update)
timer.start(interval=interval_num, iterations=iter_num)
# ---------------------------------------------------------------------------


def camera():
    """Global changes to Vispy camera position and type
        **note** This is not the same as the physical observer 'dcamera'
        arcball:
            Standard camera position; rotates around center point while
            maintaining focus on that point. view.camera.fov > 0 for arcball
        See vispy.scene.cameras for more info
    """
#    view.camera = 'turntable'
#    view.camera = 'perspective'
    view.camera = 'arcball'
    view.camera.center = (0, -dcamera, 0)
    view.camera.distance = dcamera
#   view.camera.set_range(x=(-0.5, 1))
#    fov = np.degrees(2*np.arctan(0.9/(2*dcamera))) #probably not correct, keeps size the
#    same
    view.camera.fov = (36)


camera()
# ---------------------------Vispy program execution-------------------------
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
# ---------------------------------------------------------------------------


def make_still(fname, beta, dcamera):
    """ Produces still images at a set beta
    **note: Vispy does not include the ability to take/save single frames of
    an animation. I am working on adding these features currently. For now this
    function uses a patchwork method of producing a .gif animation with two
    frames, then importing that file and saving the second frame to .png **

    Input:
        fname: str, name for save file
        beta: float, beta at which shape is transformed
    """
    fname = fname + '_' + str(dimension) + 'D' + '_b' + str(int(beta*100))
# -------------------------text and labels-----------------------------------
    text = visuals.Text(text="beta= %2.2f" % np.abs(beta), color="white",
                        pos=(-0.35, 0, -0.4), font_size=30)
    view.add(text)
    T = Transform(beta)
    if dimension == 1:
        PTlength = T.PT(linepos, dcamera, 0)
        lengthPT = np.abs((PTlength[(npoints-1)] - PTlength[0]) /
                          (linepos0[0][(npoints-1), 0] - linepos0[0][0, 0]))
        lengthPT_text = visuals.Text(text="L= %2.2f L(rest)" % lengthPT,
                                     color="white", pos=(-0.4, 0, 0),
                                     font_size=30)
        view.add(lengthPT_text)
        if LT:
            linepos1[0][:, 0] = linepos0[0][:, 0] / T.LT()[2]
            lengthLT = np.abs((linepos1[0][(npoints-1), 0] -
                               linepos1[0][0, 0]) / (
                                       linepos0[0][(npoints-1), 0] -
                                       linepos0[0][0, 0]))
            lengthLT_text = visuals.Text(text="L= %2.2f L(rest)" % lengthLT,
                                         color="white", pos=(-0.4, 0, 0.5),
                                         font_size=30)
            view.add(lengthLT_text)
    elif dimension == 3:
            textcam = visuals.Text(text="dcamera= %2.2f" % 2*dcamera,
                                   color="white", pos=(0.3, 0, -0.4),
                                   font_size=30)
            view.add(textcam)
# ---------------------------saves to file----------------------------------
    writer = imageio.get_writer(fname+'.gif')
#    size = (700, 600)
    im = canvas.render()
    writer.append_data(im)
    update(2)
    writer.close()

    reader = imageio.get_reader(fname+'.gif')
    for i in enumerate(reader):
        writer = imageio.get_writer(fname+'.png', mode='i')
        im = canvas.render()
        writer.append_data(im)
        update(2)
        writer.close()
# ---------------------------------------------------------------------------


def make_anim(fname, gif=False):
    """ Saves frames to .mp4 file with the use of Imageio as Vispy also does
    not include a built in video writer yet.

    Input:
        fname: str, savefile
        gif: bool, change to true to make .gif. **warning, very slow**
    """
    fname = fname + '_' + str(dimension) + 'D'

    def make_frame(t):
        """ Vispy default function to compile convas frames into a movie
        """
        update(t)
        gloo.clear((0, 1, 1, 0))
        canvas.on_draw(None)
        return _screenshot((0, 0, canvas.size[0], canvas.size[1]))[:, :, :3]

    animation = VideoClip(make_frame, duration=20)
    if gif:
        animation.write_gif(fname, fps=100, program='imageio')
    else:
        animation.write_videofile(fname+".mp4", fps=100)


if anim == 0:
    make_still(fname, beta, dcamera)
elif anim == 1:
    make_anim(fname)
