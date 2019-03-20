import os.path as p

import glob
from builtins import range

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

self_path = p.dirname(p.abspath(__file__))
root_path = p.dirname(self_path)

import subprocess as sub

import aronnax as aro


## Pretty plots
plt.rcParams['figure.figsize'] = (12, 12) # set default figure size to 12x12 inches
# plt.rc('text',usetex=True)
#font = {'family':'serif','size':16}
font = {'family':'serif','size':10, 'serif': ['computer modern roman']}
plt.rc('font',**font)
plt.rc('legend',**{'fontsize':8})
matplotlib.rcParams['text.latex.preamble']=[r'\usepackage{amsmath}']


nx = 400
ny = 960
layers = 1
dx = 5000
dy = 5000



def wetmask(X, Y):
    """The wet mask."""

    # start with land everywhere and carve out space for water
    wetmask = np.ones(X.shape, dtype=np.float64)

    # set land on the edges
    wetmask[ 0, :] = 0
    wetmask[-1, :] = 0
    wetmask[ :, 0] = 0
    wetmask[ :,-1] = 0

    return wetmask


grid = aro.Grid(nx, ny, layers, dx, dy)

X_h, Y_h = np.meshgrid(grid.x/1e3, grid.y/1e3)
mask_h = wetmask(X_h, Y_h)
X_v, Y_v = np.meshgrid(grid.x/1e3, grid.yp1/1e3)
mask_v = wetmask(X_v, Y_v)
X_zeta, Y_zeta = np.meshgrid(grid.xp1/1e3, grid.yp1/1e3)



def plt_vort(simulation=None):
    u_files = sorted(glob.glob("{0}output/snap.u.*".format(simulation)))
    v_files = sorted(glob.glob("{0}output/snap.v.*".format(simulation)))


    c_lim = 1

    coriolis = 4.99e-5 + Y_zeta[1:-1,1:-1]*2.15e-11

    for i in range(0, len(v_files)):
        u = aro.interpret_raw_file(u_files[i], nx, ny, layers)
        v = aro.interpret_raw_file(v_files[i], nx, ny, layers)

        zeta = (v[0,1:-1,1:] - v[0,1:-1,:-1])/dx - (u[0,1:,1:-1] - u[0,:-1,1:-1])/dy


        f, ax1 = plt.subplots(1, 1, figsize=(5,5))

        im = ax1.pcolormesh(X_zeta[1:-1,1:-1], Y_zeta[1:-1,1:-1], zeta/coriolis,
            cmap='RdBu_r',
            vmin=-c_lim, vmax=c_lim)
        CB = plt.colorbar(im, ax=ax1, orientation='vertical')
        CB.set_label('vorticity/f')

        # ax1.plot(500, 500, 'ro', ms=8)
        # ax1.set_xlim(0,1000)
        ax1.plot(200*dx/1e3,864*dy/1e3, 'ko', ms=3)
        ax1.set_aspect('equal')
        ax1.set_xlabel('x (km)')
        ax1.set_ylabel('y (km)')

        plt.title('Year {:02d} Day {:03d}'.format(
            int(np.floor(i/4/360)), int(np.mod(i/4, 360))))

        f.savefig('{}figures/vort_{:06d}.png'.format(simulation,i), dpi=300,
            bbox_inches='tight')
        plt.close('all')

    try:
        sub.check_call(["ffmpeg", "-pattern_type", "glob", "-i",
            "{0}/figures/vort_*.png".format(simulation),
            "-vcodec", "libx264", "-s", "2400x1540",
            "-pix_fmt", "yuv420p", "{0}/{1}.mp4".format(simulation, 'anim_vort')])
    except:
        print("failed to make vort animation")


if __name__ == '__main__':
    sub.check_call(["mkdir", "-p", "spin_up/figures/"])

    plt_vort('spin_up/')
