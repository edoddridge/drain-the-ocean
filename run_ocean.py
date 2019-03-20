import os.path as p

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

self_path = p.dirname(p.abspath(__file__))
root_path = p.dirname(self_path)

import aronnax.driver as drv
from aronnax.utils import working_directory


# To add the plug hole, you need to ammend model_main.f90, and add the following code at line 320

        # ! bathplug 10 m in radius

        # if (xlow <= 200 .and. xhigh>= 200) then
        #   if (ylow <= 864 .and. yhigh>= 864) then
        #     etanew(200,864) = etanew(200,864) - 10*10*pi* SQRT(2*g_vec(1)* h(200,864,1))*dt/(dx*dy)
        #   end if
        # end if

def ocean_drain():

    nx = 400
    ny = 960
    layers = 1
    dx = 5000
    dy = 5000

    

    def wetmask(X, Y):
        """The wet mask."""

        depth = bathymetry(X, Y, plot=False)

        wetmask = np.zeros(X.shape, dtype=np.float64)

        wetmask[depth>0] = 1

        # set land on the edges
        wetmask[ 0, :] = 0
        wetmask[-1, :] = 0
        wetmask[ :, 0] = 0
        wetmask[ :,-1] = 0

        return wetmask

    def bathymetry(X,Y, plot=True):

        d_max = 6000
        width_scale = 3./1000e3

        x_depth = 0.5*d_max*(np.tanh(X*width_scale) + 
                               np.tanh((X.max() - X)*width_scale))

        y_depth = (0.5*d_max*(np.tanh(Y*width_scale) + 
                               np.tanh((Y.max() - Y)*width_scale)) 
                    - np.maximum(4e2 * (4320e3-Y)/1823e3,0)
                    )

        depth =(x_depth + y_depth)/2.

        depth = depth - 2000

        depth[depth<0] = 0

        # set minimum depth to 250 m (also the model won't run if depthFile
        #   contains negative numbers)
        # depth = np.maximum(depth, 250)

        if plot:
            plt.pcolormesh(X/1e3, Y/1e3, np.ma.masked_where(depth<0, depth))
            plt.colorbar()
            plt.axes().set_aspect('equal')
            plt.savefig('depth.png', bbox_inches='tight')
            plt.close()

        return depth



    with working_directory(p.join(self_path, 'spin_up')):
        drv.simulate(
                # give it flat layers and let it squash them to fit
                initHfile=[4000],
                wetMaskFile=[wetmask],
                depthFile=[bathymetry],
                nx=nx, ny=ny, dx=dx, dy=dy,
                exe='aronnax_external_solver', 
                dt=50, nTimeSteps=12441600)

if __name__ == '__main__':
    ocean_drain()
