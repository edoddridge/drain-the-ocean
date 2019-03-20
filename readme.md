# Drain the ocean

This simulation is a one layer ocean-sized bathtub, with a 10 m radius plug hole near the northern end.

The simulation uses Aronnax (https://github.com/edoddridge/aronnax). But, ocean models don't generally come with a plug, so you need to modify the source code. Add the following code snippet at line 320 of `model_main.f90`

```
        ! bathplug 10 m in radius

        if (xlow <= 200 .and. xhigh>= 200) then
          if (ylow <= 864 .and. yhigh>= 864) then
            etanew(200,864) = etanew(200,864) - 10*10*pi* SQRT(2*g_vec(1)* h(200,864,1))*dt/(dx*dy)
          end if
        end if
```

After that, you just need to have Aronnax installed and run the python script `run_ocean.py`, which will launch the simulation on 32 processors.
