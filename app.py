import paraview.web.venv
from pathlib import Path
from paraview import simple

from trame.app import get_server
from trame.widgets import vuetify
from trame.ui.vuetify import SinglePageWithDrawerLayout
import subprocess


monoalg_command = "./runmonoalg.sh"

#Inicializa o servidor
server = get_server()
state, ctrl = server.state, server.controller

time_step = 0
step = 0

def callback(mesh, Scalars_):
    print("Clicou")



@ctrl.add("on_server_reload")
def print_item(item):
    print("Clicked on", item)

def updateMesh():
    print("a")
    pass
#Isso é exclusivo do código do cone, mas achei interessante salvar: ele modifica as coisas sempre que sofre alguma mudança
@state.change("position")
def update_contour(position , **kwargs):
    print("a")

def subTime():
    print("a")
    pass

def addTime():
    pass

def runMonoAlg3D():
    #Colocar os campos 
    with open("./MonoAlg3D_C/example_configs/custom.ini", 'w') as file:
        file.write("[main]\nnum_threads=6\ndt_pde=0.02\nsimulation_time=" + str(state.simulation_time) + "\n")
        file.write("abort_on_no_activity=false\nuse_adaptivity=false\n[update_monodomain]\nmain_function=update_monodomain_default\n[save_result]\nprint_rate=50\noutput_dir=./outputs/temp\nmain_function=save_as_vtu\ninit_function=init_save_as_vtk_or_vtu\nend_function=end_save_as_vtk_or_vtu\nsave_pvd=true\nfile_prefix=V\n[assembly_matrix]\ninit_function=set_initial_conditions_fvm\nsigma_x=0.0000176\nsigma_y=0.0001334\nsigma_z=0.0000176\nlibrary_file=shared_libs/libdefault_matrix_assembly.so\nmain_function=homogeneous_sigma_assembly_matrix\n[linear_system_solver]\ntolerance=1e-16\nuse_gpu=yes\nmax_iterations=200\nlibrary_file=shared_libs/libdefault_linear_system_solver.so\nmain_function=conjugate_gradient\ninit_function=init_conjugate_gradient\nend_function=end_conjugate_gradient\n[alg]\nrefinement_bound = 0.11\nderefinement_bound = 0.10\nrefine_each = 1\nderefine_each = 1\n[domain]\nname=Plain Mesh\nnum_layers=1\nstart_dx=100.0\nstart_dy=100.0\nstart_dz=100.0\nside_length=10000\nmain_function=initialize_grid_with_square_mesh\n[ode_solver]\ndt=0.02\nuse_gpu=yes\ngpu_id=0\nlibrary_file=shared_libs/libten_tusscher_3_epi.so\n")
        file.write("[stim_1]\nstart =" + str(state.S1) +"\nduration=2.0\ncurrent=-50.0\nmin_x=250.0\nmax_x=500.0\nmin_y=0.0\nmax_y=1000.0\nmain_function=stim_x_y_limits")
        if(state.S2!=0):
            file.write("\n[stim_2]\nstart =" + str(state.S2) +"\nduration=2.0\ncurrent=-50.0\nmin_x=0.0\nmax_x=250.0\nmin_y=0.0\nmax_y=1000.0\nmain_function=stim_x_y_limits")

    saida = subprocess.check_output(monoalg_command, shell=True, universal_newlines=True)
    print(saida)
    pass

with SinglePageWithDrawerLayout(server) as layout:
    with layout.drawer:
        vuetify.VTextField(v_model=("simulation_time", 1000))
        vuetify.VTextField(v_model=("S1", 5))
        vuetify.VTextField(v_model=("S2" , 500))

        vuetify.VBtn("Executar", click=runMonoAlg3D)    
    with layout.toolbar:
        vuetify.VSpacer()

        #slider do tempo
        vuetify.VSlider(
            v_model=("position", 0),
            min=0,
            max=100,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
            # change=ctrl.view_update,
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
                    )
        vuetify.VBtn("+",
                     click=addTime) 
        vuetify.VBtn("*", click=updateMesh)

    #Isso é a parte inferior e maior da página (onde tudo é plotado por enquanto)
            


#Inicia o servidor
server.start()
