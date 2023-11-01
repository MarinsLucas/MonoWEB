import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify
from trame.widgets import html
from vtkmodules.vtkFiltersSources import vtkConeSource

pv.OFF_SCREEN = True

#Inicializa o servidor
server = get_server()
state, ctrl = server.state, server.controller

#Tenho que modificar essa linha
reader = pv.get_reader('temp/simulation_result.pvd')
reader.set_active_time_value(reader.time_values[0])
source = reader.read()
current_time = reader.time_values[0]
#Cria barra de escala interativa
sargs = dict(interactive=True) 
#https://docs.pyvista.org/version/stable/examples/02-plot/scalar-bars.html

#Utiliza o plotter do pyvista para plotar a mesh.
pl = pv.Plotter()
pl.add_mesh(source, scalar_bar_args=sargs, clim=[-90, 40], name="mesh")

step = 0
#Isso é exclusivo do código do cone, mas achei interessante salvar: ele modifica as coisas sempre que sofre alguma mudança
@state.change("time_step")
def update_contour(time_step, **kwargs):
    reader.set_active_time_value(reader.time_values[int(time_step)])
    current_time = reader.time_values[int(time_step)]
    source = reader.read()
    pl.add_mesh(source, scalar_bar_args=sargs, clim=[-90, 40], name="mesh")
    step = time_step
    ctrl.view_update()

def subTime():
    print(step)
    """ reader.set_active_time_value(reader.time_values[int(current_time-1)])
    current_time = reader.time_values[int(current_time-1)]
    source = reader.read()
    pl.add_mesh(source, scalar_bar_args=sargs, clim=[-90, 40], name="mesh")
    ctrl.view_update() """

with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()

        #slider do tempo
        vuetify.VSlider(
            v_model=("time_step", 0),
            min=0,
            max=len(reader.time_values)-1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
            change=ctrl.view_update,
            messages = current_time,
        )
    
        #Barra de carregamento abaixo do header
        vuetify.VProgressLinear(
            indeterminate=True,
            absolute=True,
            bottom=True,
            active=("trame__busy",),
        )

        #Estava tentando colocar um icone, mas não consigo.
        #https://vuetifyjs.com/en/api/v-btn/#props
        vuetify.VBtn("-",
                    click=subTime,
                    messages = current_time,
                    change=ctrl.view_update,
                    )
        vuetify.VBtn("▶")
        vuetify.VBtn("+") 

    #Isso eu nn entendi, mas todo código com trame tem isso
    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # Utiliza a UI do pyvista (onde dá opções pra resetar a camera e etc)
            view = plotter_ui(pl)
            ctrl.view_update = view.update

#Inicia o servidor
server.start()
