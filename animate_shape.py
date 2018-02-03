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


# Canvas setup
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True, resizable=True)
view = canvas.central_widget.add_view()

# Initial shape data
dimension = 3
cube = Make_shape(dimension)
verts = cube.verts()
linepos = cube.frame(verts, 50) 
linepos0 = cube.frame(verts, 50)  # static line positions
# Adds initial visuals to shape data
scatter = visuals.Markers()
scatter.set_data(verts, edge_color=None, face_color=(1, 1, 1, .5), size=10)
view.add(scatter)

lines = np.empty(0,)
for k in range(len(linepos)):
    result = np.array([visuals.LinePlot(linepos[k], color='cyan', width=2,
                                        marker_size=0, connect="segments")])
    lines = np.append(lines, result, axis=0)
for j in range(len(lines)):
    view.add(lines[j])

axis = visuals.XYZAxis(parent=view.scene)

beta = 0
tid = 0


# Animation of visuals
# need to make beta decrease after some time value to make a nice looping
# .gif. Below is correct
def update(ev):
    global verts, scatter, linepos, beta, tid, iter_num

    if tid < np.around(((iter_num / 2) - 1), decimals=1):
        beta += 0.001
    elif tid > np.around((iter_num / 2), decimals=1):
        beta -= 0.001

    T = Transform(beta)
    tid += 1
    verts += 0
    d = 0.5

    if dimension == 1:
        linepos[0][:, 0] = T.DT(linepos0, d, 0)
    elif dimension == 2:
        for k in range(4):
            linepos[k][:, 0] = T.DT(linepos0, d, k)
    elif dimension == 3:
        for k in range(len(lines)):
            linepos[k][:, 0] = T.DT(linepos0, d, k)
#        linepos[0][:, 0] = T.DT(linepos0, d, 0)
#        linepos[1][:, 0] = T.DT(linepos0, d, 1)
#        linepos[2][:, 0] = T.DT(linepos0, d, 2)
#        linepos[3][:, 0] = T.DT(linepos0, d, 3)
#        linepos[4][:, 0] = T.DT(linepos0, d, 4)
#        linepos[5][:, 0] = T.DT(linepos0, d, 5)
#        linepos[6][:, 0] = T.DT(linepos0, d, 6)
#        linepos[7][:, 0] = T.DT(linepos0, d, 7)
#        linepos[8][:, 0] = T.DT(linepos0, d, 8)
#        linepos[9][:, 0] = T.DT(linepos0, d, 9)
#        linepos[10][:, 0] = T.DT(linepos0, d, 10)
#        linepos[11][:, 0] = T.DT(linepos0, d, 11)
    for j in range(len(lines)):
        if j in [2, 5, 9, 10]:
            lines[j].set_data(linepos[j], marker_size=0, color='red')
        else:
            lines[j].set_data(linepos[j], marker_size=0, color='cyan')
    scatter.set_data(pos=verts)


total_time = 10
iter_num = 2000
interval_num = total_time / iter_num
timer = app.Timer()
timer.connect(update)
timer.start(interval=interval_num, iterations=iter_num)

# Setup of camera
# view.camera = 'turntable'
# view.camera = 'perspective'
view.camera = 'arcball'
view.camera.center = (0.5, 0.5, 0.5)
view.camera.distance = 100
#view.camera.set_range(x=(-0.5, 1)) #  This does change in the .gif
view.camera.fov = (1) # tilts view, needs to be >0 for arcball

# Runs animation
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()

# #Writes animation to file
#    def make_frame(t):
#        update(t)
#        gloo.clear((0,1,1,0))
#        canvas.on_draw(None)
#        return _screenshot((0, 0, canvas.size[0], canvas.size[1]))[:, :, :3]
#
#animation = VideoClip(make_frame, duration=20)
##animation.write_gif("anim_SRcube1.gif", fps=100, program='imageio')  # export as GIF (slow)
#animation.write_videofile("anim_SRhrod.mp4", fps=100)  # export as video
        
# This can be used for shitty animation if necessary
#n_steps = 100
#writer = imageio.get_writer('animation5.gif')
#for i in range(n_steps * 2):
#    im = canvas.render()
#    writer.append_data(im)
#    if i >= n_steps:
#        update(i)
#    else:
#        pass
#writer.close()
