import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.widgets import vuetify
from trame.ui.vuetify import SinglePageWithDrawerLayout
import subprocess

reader = pv.get_reader('MonoAlg3D_C/outputs/temp/simulation_result.pvd')
reader.set_active_time_value(reader.time_values[10])
source = reader.read()
print(source[0].array_names)
print(source[0].n_points)
print(source[0].get_array('Scalars_'))