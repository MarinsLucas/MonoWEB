import sys
if '--virtual-env' in sys.argv:
  virtualEnvPath = sys.argv[sys.argv.index('--virtual-env') + 1]
  # Linux
  #virtualEnv = virtualEnvPath + '/bin/activate_this.py'
  # Windows
  virtualEnv = virtualEnvPath + '/Scripts/activate_this.py'
  if sys.version_info.major < 3:
    execfile(virtualEnv, dict(__file__=virtualEnv))
  else:
    exec(open(virtualEnv).read(), {'__file__': virtualEnv})


import paraview.web.venv
from pathlib import Path
from paraview import simple

from trame.app import get_server
from trame.widgets import vuetify, paraview
from trame.ui.vuetify import SinglePageWithDrawerLayout
import subprocess


monoalg_command = "./runmonoalg.sh"
########################### Configuando paraview #######################
# -----------------------------------------------------------------------------
# ParaView pipeline
# -----------------------------------------------------------------------------
from paraview import simple

simple.LoadDistributedPlugin("AcceleratedAlgorithms", remote=False, ns=globals())
# reader = simple.XMLUnstructuredGridReader(FileName="/home/user/venv/MonoAlgWeb-trame/MonoAlg3D_C/outputs/temp/V_it_0.vtu")
reader = simple.PVDReader(FileName="C:/Users/lucas/venv/MonoAlgWeb-trame/MonoAlg3D_C/outputs/temp/simulation_result.pvd")
reader.CellArrays = ['Scalars_']
#reader.TimeArray = "Alguma coisa"

# Rendering setup
view = simple.GetRenderView()
view.OrientationAxesVisibility = 0
view = simple.Render()
representation = simple.Show(reader, view)
simple.ResetCamera()
view.CenterOfRotation = view.CameraFocalPoint
########################################## Fim #################################

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


#Não consegui testar isso ainda (pois minha simulação é muito pequena)
def PlayPVD():
    animationscene = simple.GetAnimationScene()
    """     animationscene.Play()
    html_view.update_image() """
    for i in range(10):
        animationscene.GoToNext()
        html_view.update_image()
        html_view.update
    pass

def update_frame():
    print(state.currentTime)
    animationscene = simple.GetAnimationScene()
    animationscene.AnimationTime = float(state.currentTime)
    html_view.update_image()
    pass

@state.change("position")
def update_contour(position , **kwargs):
    animationscene = simple.GetAnimationScene()
    animationscene.AnimationTime = position
    html_view.update_image()
    pass

def subTime():
    animationscene = simple.GetAnimationScene()
    animationscene.GoToPrevious()
    html_view.update_image()
    pass

def addTime():
    animationscene = simple.GetAnimationScene()
    animationscene.GoToNext()
    print(animationscene.TimeStep)
    html_view.update_image()
    state.currentTime = animationscene.AnimationTime
    pass

def lastTime():
    animationscene = simple.GetAnimationScene()
    animationscene.GoToLast()
    html_view.update_image()
    pass

def firstTime():
    animationscene = simple.GetAnimationScene()
    animationscene.GoToFirst()
    html_view.update_image()
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
   
        #Barra de carregamento abaixo do header
        vuetify.VProgressLinear(
            indeterminate=True,
            absolute=True,
            bottom=True,
            active=("trame__busy",),
        )

        #Estava tentando colocar um icone, mas não consigo.
        #https://vuetifyjs.com/en/api/v-btn/#props
        vuetify.VBtn("F", click=firstTime)
        vuetify.VBtn("-",
                    click=subTime,
                    )
        
        vuetify.VTextField(v_model=("currentTime", 0), change=update_frame, number = True)

        vuetify.VBtn("+",
                     click=addTime) 
        #Tirei o botão que fazia a animação, porque eu não consegui fazer a animação (talvez estudar mais o paraview em si?)
        #vuetify.VBtn("*", click=PlayPVD)
        vuetify.VBtn("L", click=lastTime)

    #Isso é a parte inferior e maior da página (onde tudo é plotado por enquanto)
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            html_view = paraview.VtkRemoteLocalView(
                view,
                namespace="demo",
            )
            ctrl.view_update = html_view.update
            ctrl.view_reset_camera = html_view.reset_camera

#Inicia o servidor
server.start()
