""" 
TODO list:
Essencial
- Rodar o MonoAlg3D!!!
- Consertar passo de tempo
- Consertar animação
- Consertar colormap
- Leitura de estímulos do arquivo

Ideal
- Exibição dos exemplos sem execução do MonoAlg3D
- Seleção de célula
- Gerar gráfico

Seria bom:
- Clip
"""


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

import asyncio

import paraview.web.venv
from pathlib import Path
from paraview import simple
from paraview.selection import *

from trame.app import get_server, asynchronous
from trame.widgets import paraview, plotly
from trame.ui.vuetify import SinglePageWithDrawerLayout
import subprocess
import plotly.graph_objects as go
from trame.widgets import vuetify2 as vuetify
import threading
import time
import re

monoalg_command = "./runmonoalg.sh"
########################### Configuando paraview #######################
# -----------------------------------------------------------------------------
# ParaView pipeline
# -----------------------------------------------------------------------------
from paraview import simple

simple.LoadDistributedPlugin("AcceleratedAlgorithms", remote=False, ns=globals())

# Rendering setup
view = simple.GetRenderView()
view.OrientationAxesVisibility = 0
view = simple.Render()
simple.ResetCamera()
view.CenterOfRotation = view.CameraFocalPoint
########################################## Fim #################################

#Inicializa o servidor
server = get_server()
server.client_type = "vue2"

state, ctrl = server.state, server.controller

animationscene = simple.GetAnimationScene()
timekeeper = animationscene.TimeKeeper
metadata = None
time_values = []
show_graph = False
domain_matrix_main_function_options = ["initialize_grid_with_cuboid_mesh", "initialize_grid_with_spherical_mesh", "initialize_grid_with_square_mesh", "initialize_grid_with_cable_mesh", "initialize_grid_with_rabbit_mesh",
                                        "initialize_grid_with_plain_fibrotic_mesh",  "initialize_grid_with_plain_source_sink_fibrotic_mesh", 
                                       "initialize_grid_with_plain_and_sphere_fibrotic_mesh", "initialize_grid_with_cuboid_and_sphere_fibrotic_mesh", "initialize_grid_with_plain_and_sphere_fibrotic_mesh_without_inactivating", "initialize_grid_with_square_mesh_and_fibrotic_region",
                                        "initialize_grid_with_square_mesh_and_source_sink_fibrotic_region"]

library_file_options = ["shared_libs/libToRORd_dynCl_mixed_endo_mid_epi.so", "shared_libs/libmitchell_shaeffer_2003.so", "shared_libs/libstewart_aslanidi_noble_2009.so", "shared_libs/libten_tusscher_2006.so", "shared_libs/libohara_rudy_endo_2011.so",
                        "shared_libs/libbondarenko_2004.so", "shared_libs/libcourtemanche_ramirez_nattel_1998.so", "shared_libs/libfhn_mod.so", "shared_libs/libMaleckar2008.so", "shared_libs/libMaleckar2009.so", "shared_libs/libToRORd_fkatp_mixed_endo_mid_epi.so",
                        "shared_libs/libToRORd_fkatp_endo.so", "shared_libs/libten_tusscher_3_endo.so", "shared_libs/libten_tusscher_2004_endo.so", "shared_libs/libToRORd_Land_mixed_endo_mid_epi.s" ]

stimuli_main_function_options = ["stim_if_x_less_than", "stim_if_y_less_than", "stim_if_z_less_than", "stim_if_x_greater_equal_than","stim_if_y_greater_equal_than", "stim_if_z_greater_equal_than", "stim_sphere",  "stim_x_y_limits", "stim_x_y_z_limits",
                                 "stim_if_inside_circle_than" ]

examples_options = ["EX01_plain_mesh_healthy.ini", "EX02_plain_mesh_S1S2_protocol.ini", "EX03_plain_mesh_with_ischemia.ini", "EX04_3dwedge_healthy.ini"]
#Variáveis dos estímulos:
stimuli_main_function_selected_dicionary = {}

def thread_play():
    while state.play == True:
        print("Thread em execução...")
        time.sleep(10)

threadPlay = threading.Thread(target=thread_play)

state.n_estimulos = 0
# Load function, runs every time server starts
def load_data(**kwargs):
    global time_values, representation, reader, show_graph
    reader = simple.PVDReader(FileName="./MonoAlg3D_C/outputs/temp/simulation_result.pvd")
    reader.CellArrays = ['Scalars_']
    reader.UpdatePipeline()
    representation = simple.Show(reader, view)
    time_values = list(timekeeper.TimestepValues)
    
    state.time_value = time_values[0]
    state.times =len(time_values)-1
    state.time = 0
    state.play = False
    state.printRate = 10 #default = 1
    simple.ResetCamera()
    view.CenterOfRotation = view.CameraFocalPoint
    state.n_estimulos = 0
    
    
@ctrl.add("on_server_reload")
def print_item(item):
    print("Clicked on", item)

@state.change("time")
def update_time(time, **kwargs):
    if len(time_values) == 0:
        return  
    
    if time >= len(time_values):
        time = 0
        state.time = time
        state.play = False
    time_value = time_values[time]
    timekeeper.Time = time_value
    state.time_value = time_value
    
    html_view.update_image()

global html_view

@state.change("play")
@asynchronous.task 
async def update_play(**kwargs):
    while state.play:
        with state:
            state.time += int(state.printRate)
            update_time(state.time)

        await asyncio.sleep(0.1)

def update_frame():
    #Eu tenho o valor do tempo, de verdade
    #preciso tranformar na iteração
    dt = time_values[1] - time_values[0]
    state.time = int(float(state.time_value)/dt)
    html_view.update_image()
    pass

@state.change("position")
def update_contour(position , **kwargs):
    # animationscene = simple.GetAnimationScene()
    animationscene.AnimationTime = position
    html_view.update_image()
    pass

def subTime():
    state.time -= int(state.printRate)
    html_view.update_image()
    pass

def addTime():
    state.time += int(state.printRate)
    html_view.update_image()
    pass

def lastTime():
    state.time = state.times
    html_view.update_image()
    pass

def firstTime():
    state.time = 0
    html_view.update_image()
    pass

def addstim():
    state.n_estimulos +=1
    if(state.n_estimulos > 10):
        state.n_estimulos = 10
    pass

def removestim():
    state.n_estimulos -= 1
    if state.n_estimulos < 0: 
        state.n_estimulos = 0
    pass

def clearstims():
    state.n_estimulos = 0
    pass

def addClip():
    clip = simple.Clip(registrationName="Clip1",Input=reader)
    clip.ClipType = "Plane"
    clip.HyperTreeGridClipper = 'Plane'
    clip.Scalars = ['CELLS', 'Scalars_']
    clip.Value = -85.2300033569336
    clip.Invert = 1
    clip.Crinkleclip = 0
    clip.Exact = 0

    clip.ClipType.Origin = [16375.0, 15125.0, 13875.0]
    clip.ClipType.Normal = [1.0, 0.0, 0.0]
    clip.ClipType.Offset = 0.0

    clip.HyperTreeGridClipper.Origin = [16375.0, 15125.0, 13875.0]
    clip.HyperTreeGridClipper.Normal = [1.0, 0.0, 0.0]
    clip.HyperTreeGridClipper.Offset = 0.0


def playAnimation():
    if state.play:
        state.play = False
    else:
        state.play = True

def readini(nome_arquivo):
    config = {}
    with open("./MonoAlg3D_C/example_configs/" + str(nome_arquivo), 'r') as file:
        current_section = None
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.match(r'\[(\w+)\]', line)
            if match:
                current_section = match.group(1)
                config[current_section] = {}
            else:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    config[current_section][key.strip()] = value.strip()

    state.simulation_time = config["main"]["simulation_time"]
    state.print_rate = config["save_result"]["print_rate"]
    state.sigma_x = config["assembly_matrix"]["sigma_x"]
    state.sigma_y = config["assembly_matrix"]["sigma_y"]
    state.sigma_z = config["assembly_matrix"]["sigma_z"]
    state.domain_name = config["domain"]["name"]
    state.start_dx = config["domain"]["start_dx"]
    state.start_dy = config["domain"]["start_dy"]
    state.start_dz = config["domain"]["start_dz"]
    
    state.domain_matrix_main_function_selected = config["domain"]["main_function"]
    #read domain variáveis
    if state.domain_matrix_main_function_selected == "initialize_grid_with_cuboid_mesh":
        state.side_length_x = config["domain"]["side_length_x"]
        state.side_length_y = config["domain"]["side_length_y"]
        state.side_length_z = config["domain"]["side_length_z"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_spherical_mesh":
        state.diameter = config["domain"]["diameter"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_cable_mesh":
        state.cable_length = config["domain"]["cable_length"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_rabbit_mesh" or state.domain_matrix_main_function_selected  == "initialize_grid_with_benchmark_mesh":
        state.maximum_discretization = config["domain"]["maximum_discretization"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_fibrotic_mesh":
        state.seed = config["domain"]["seed"]
        state.phi = config["domain"]["phi"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_source_sink_fibrotic_mesh":
        state.channel_width = config["domain"]["channel_width"]
        state.channel_length = config["domain"]["channel_length"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh":
        state.phi = config["domain"]["phi"]
        state.plain_center = config["domain"]["plain_center"]
        state.sphere_radius = config["domain"]["sphere_radius"]
        state.border_zone_radius = config["domain"]["border_zone_radius"]
        state.border_zone_size = config["domain"]["border_zone_size"]
        state.seed = config["domain"]["seed"] #optional
    if state.domain_matrix_main_function_selected == "initialize_grid_with_cuboid_and_sphere_fibrotic_mesh":
        state.phi = config["domain"]["phi"]
        state.sphere_center = config["domain"]["sphere_center"] #optional
        state.sphere_radius = config["domain"]["sphere_radius"]
        state.seed = config["domain"]["seed"] #optional
    if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh_without_inactivating":
        state.phi = config["domain"]["phi"]
        state.plain_center = config["domain"]["plain_center"]
        state.border_zone_radius = config["domain"]["border_zone_radius"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh_and_fibrotic_region":
        state.phi = config["domain"]["phi"]
        state.seed = config["domain"]["seed"]
        state.region_min_x = config["domain"]["region_min_x"]
        state.region_max_x = config["domain"]["region_max_x"]
        state.region_min_y = config["domain"]["region_min_y"]
        state.region_max_y = config["domain"]["region_max_y"]
        state.region_min_z = config["domain"]["region_min_z"]
        state.region_max_z = config["domain"]["region_max_z"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh_and_source_sink_fibrotic_region":
        state.phi = config["domain"]["phi"]
        state.seed = config["domain"]["seed"] #optional
        state.region_min_x = config["domain"]["region_min_x"]
        state.region_max_x = config["domain"]["region_max_x"]
        state.region_min_y = config["domain"]["region_min_y"]
        state.region_max_y = config["domain"]["region_max_y"]
        state.region_min_z = config["domain"]["region_min_z"]
        state.region_max_z = config["domain"]["region_max_z"]
        state.source_sink_min_x = config["domain"]["source_sink_min_x"]
        state.source_sink_max_x = config["domain"]["source_sink_max_x"]
        state.side_length = config["domain"]["side_length"]
    if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh":
        state.side_length = config["domain"]["side_length"]


    state.library_file_select = config["ode_solver"]["library_file"]

    state.n_estimulos = 0
    for section in config.values():
        for key in section.keys():
            if key.startswith('stim'):
                state.n_estimulos += 1
                print(state.n_estimulos)



def runMonoAlg3D():
    #Colocar os campos 
    with open("./MonoAlg3D_C/example_configs/custom.ini", 'w') as file:
        #MAIN
        file.write("[main]\nnum_threads=6\ndt_pde=0.02\nsimulation_time=" + str(state.simulation_time) + "\nabort_on_no_activity=true\nuse_adaptivity=false\n")

        #Update Monodomain
        file.write("[update_monodomain]\nmain_function=update_monodomain_default\n")
        
        #print_rate
        file.write("[save_result]\nprint_rate=" + str(state.print_rate) + "\noutput_dir=./outputs/temp\nmain_function=save_as_vtu\ninit_function=init_save_as_vtk_or_vtu\nend_function=end_save_as_vtk_or_vtu\nsave_pvd=true\nfile_prefix=V\n")
        
        #assembly matrix
        file.write("[assembly_matrix]\ninit_function=set_initial_conditions_fvm\nsigma_x="+str(state.sigma_x)+"\nsigma_y="+str(state.sigma_y)+ "\nsigma_z="+ str(state.sigma_z) + "\nmain_function=homogeneous_sigma_assembly_matrix\n")
        
        #linear system solver
        file.write("[linear_system_solver]\ntolerance=1e-16\nuse_preconditioner=no\nmax_iterations=200\nuse_gpu=true\ninit_function=init_conjugate_gradient\nend_function=end_conjugate_gradient\nmain_function=conjugate_gradient\n")

        #domain
        file.write("[domain]\nname=" + str(state.domain_name) + "\nstart_dx=" + str(state.start_dx) + "\nstart_dy=" + str(state.start_dy) + "\nstart_dz=" + str(state.start_dz)+ "\nmain_function=" + str(state.domain_matrix_main_function_selected))
        
        if state.domain_matrix_main_function_selected == "initialize_grid_with_cuboid_mesh":
            file.write("\nside_length_x=" + str(state.side_length_x))
            file.write("\nside_length_y="+str(state.side_length_y))
            file.write("\nside_length_z=" + str(state.side_length_z))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_spherical_mesh":
            file.write("\ndiameter="+str(state.diameter))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_cable_mesh":
            file.write("\ncable_length="+str(state.cable_length))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_rabbit_mesh" or state.domain_matrix_main_function_selected  == "initialize_grid_with_benchmark_mesh":
            file.write("\nmaximum_discretization="+str(state.maximum_discretization))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_fibrotic_mesh":
            file.write("\nseed="+str(state.seed))
            file.write("\nphi="+str(state.phi))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_source_sink_fibrotic_mesh":
            file.write("\nchannel_width=" + str(state.channel_width))
            file.write("\nchannel_length="+str(state.channel_length))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh":
            file.write("\nphi="+str(state.phi))
            file.write("\nplain_center="+ str(state.plain_center))
            file.write("\nsphere_radius="+str(state.sphere_radius))
            file.write("\nborder_zone_radius="+str(state.border_zone_radius))
            file.write("\nborder_zone_size="+str(float(state.border_zone_radius) - float(state.sphere_radius)))
            file.write("\nseed="+str(state.seed))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_cuboid_and_sphere_fibrotic_mesh":
            file.write("\nphi="+str(state.phi))
            file.write("\nsphere_center="+str(state.sphere_center))
            file.write("\nsphere_radius="+str(state.sphere_radius))
            file.write("\nseed="+str(state.seed))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh_without_inactivating":
            file.write("\nphi="+str(state.phi))
            file.write("\nplain_center="+str(state.plain_center))
            file.write("\nborder_zone_radius="+str(state.border_zone_radius))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh_and_fibrotic_region":
            file.write("\nphi="+str(state.phi))
            file.write("\nseed="+str(state.seed))
            file.write("\nregion_min_x="+ str(state.region_min_x))
            file.write("\nregion_max_x=" +str(state.region_max_x))
            file.write("\nregion_min_y="+str(state.region_min_y))
            file.write("\nregion_max_y="+str(state.region_max_y))
            file.write("\nregion_min_z="+str(state.region_min_z))
            file.write("\nregion_max_z="+str(state.region_max_z))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh_and_source_sink_fibrotic_region":
            file.write("\nphi="+str(state.phi))
            file.write("\nseed="+str(state.seed))
            file.write("\nregion_min_x="+ str(state.region_min_x))
            file.write("\nregion_max_x=" +str(state.region_max_x))
            file.write("\nregion_min_y="+str(state.region_min_y))
            file.write("\nregion_max_y="+str(state.region_max_y))
            file.write("\nregion_min_z="+str(state.region_min_z))
            file.write("\nregion_max_z="+str(state.region_max_z))
            file.write("\nsource_sink_min_x="+str(state.source_sink_min_x))
            file.write("\nsource_sink_max_x="+str(state.source_sink_max_x))
            file.write("\nside_length="+str(state.side_length))
        if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh":
            file.write("\nside_length="+str(state.side_length))

        #ode_solver
        file.write("\n[ode_solver]\ndt=0.02\nuse_gpu=yes\ngpu_id=0\nlibrary_file="+str(state.library_file_select))

        #stim
        for i in range(state.n_estimulos):
            file.write("\n[stim_"+str(i)+ "]\n")
            file.write("start="+str(state["start_stim_" + str(i)]))
            file.write("\nduration="+str(state["duration_"+str(i)]))
            file.write("\ncurrent="+str(state["current_"+str(i)]))
            file.write("\nmain_function="+str(state["stimuli_main_function_selected"+str(i)]))
            if state["stimuli_main_function_selected"+str(i)] == "stim_if_x_less_than":
                file.write("\nx_limit="+str(state["x_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_y_less_than":
                file.write("\ny_limit="+str(state["y_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_z_less_than":
                file.write("\nz_limit="+str(state["z_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_x_greater_equal_than":
                file.write("\nx_limit="+str(state["x_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_y_greater_equal_than":
                file.write("\ny_limit="+str(state["y_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_z_greater_equal_than":
                file.write("\nz_limit="+str(state["z_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_sphere":
                file.write("\ncenter_x="+str(state["center_x"+str(i)]))
                file.write("\ncenter_y="+str(state["center_y"+str(i)]))
                file.write("\ncenter_z="+str(state["center_z"+str(i)]))
                file.write("\nradius="+str(state["radius"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_x_y_limits":
                file.write("\nmax_x="+str(state["max_x"+str(i)]))
                file.write("\nmin_x="+str(state["min_x"+str(i)]))
                file.write("\nmax_y="+str(state["max_y"+str(i)]))
                file.write("\nmin_y="+str(state["min_y"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_x_y_z_limits":
                file.write("\nmax_x="+str(state["max_x"+str(i)]))
                file.write("\nmin_x="+str(state["min_x"+str(i)]))
                file.write("\nmax_y="+str(state["max_y"+str(i)]))
                file.write("\nmin_y="+str(state["min_y"+str(i)]))
                file.write("\nmax_z="+str(state["max_z"+str(i)]))
                file.write("\nmin_z="+str(state["min_z"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_inside_circle_than":
                file.write("\ncenter_x="+str(state["center_x"+str(i)]))
                file.write("\ncenter_y="+str(state["center_y"+str(i)]))
                file.write("\ncenter_z="+str(state["center_z"+str(i)]))
                file.write("\nradius="+str(state["radius"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_id_less_than":
                file.write("\nid_limit="+str(state["id_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_if_id_greater_than":
                file.write("\nid_limit="+str(state["id_limit"+str(i)]))

            if state["stimuli_main_function_selected"+str(i)] == "stim_concave":
                file.write("\nmax_x_1="+str(state["max_x_1"+str(i)]))
                file.write("\nmin_x_1="+str(state["min_x_1"+str(i)]))
                file.write("\nmax_y_1="+str(state["max_y_1"+str(i)]))
                file.write("\nmin_y_1="+str(state["min_y_1"+str(i)]))
                file.write("\nmax_x_2="+str(state["max_x_2"+str(i)]))
                file.write("\nmin_x_2="+str(state["min_x_2"+str(i)]))
                file.write("\nmax_y_2="+str(state["max_y_2"+str(i)]))
                file.write("\nmin_y_2="+str(state["min_y_2"+str(i)]))
    saida = subprocess.check_output(monoalg_command, shell=True, universal_newlines=True)
    print(saida)
    pass


@state.change("example_selected")
def change_example(example_selected, **kwargs):
    readini(example_selected)

@state.change("advanced_config")
@state.change("domain_matrix_main_function_selected")
@state.change("n_estimulos")
@state.change("stimuli_main_function_selected1")
@state.change("stimuli_main_function_selected2")
@state.change("stimuli_main_function_selected3")
@state.change("stimuli_main_function_selected4")
@state.change("stimuli_main_function_selected5")
@state.change("stimuli_main_function_selected6")
@state.change("stimuli_main_function_selected7")
@state.change("stimuli_main_function_selected8")
@state.change("stimuli_main_function_selected9")
@state.change("stimuli_main_function_selected0")
def s0(**kwargs):
    update_domain_params()

def update_domain_params():
    with SinglePageWithDrawerLayout(server) as layout:
        
        layout.title.set_text("MonoWEB")

        with layout.drawer:

            vuetify.VSelect(
                items=("examples_options", examples_options),
                label="Examples",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-5",
                v_model=("example_selected", "EX01_plain_mesh_healthy.ini"),
            ) 

            #Main: simulation_time só
            vuetify.VTextField(
                v_model=("simulation_time", 1000), 
                hint="Simulation time", 
                persistent_hint=True,
            )
            
            vuetify.VCheckbox(v_model=("advanced_config", False), label="Advanced Settings")

            if state.advanced_config == True:
                #save_result: print_rate
                vuetify.VTextField(v_model=("print_rate", 1000), hint="Save rate", persistent_hint=True)

                with vuetify.VList(classes="pt-5"):
                    vuetify.VSubheader("Conductivity")
                #assembly_matrix
                vuetify.VTextField(v_model=("sigma_x", 1000), hint="Sigma X", persistent_hint=True)
                vuetify.VTextField(v_model=("sigma_y", 1000), hint="Sigma Y", persistent_hint=True)
                vuetify.VTextField(v_model=("sigma_z", 1000), hint="Sigma Z", persistent_hint=True)
            
                with vuetify.VList(classes="pt-5"):
                    vuetify.VSubheader("Domain")

                vuetify.VSelect(
                    label="Domain Main Function",
                    v_model=("domain_matrix_main_function_selected", "intialize_grid_with_cuboid_mesh"),
                    items=("domain_matrix_main_function_options", domain_matrix_main_function_options),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-5",
                ) 

                vuetify.VTextField(v_model=("start_dx", 1000), hint="Start dx", persistent_hint=True)
                vuetify.VTextField(v_model=("start_dy", 1000), hint="Start dy", persistent_hint=True)
                vuetify.VTextField(v_model=("start_dz", 1000), hint="Start dz", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_cuboid_mesh":
                    vuetify.VTextField(v_model=("side_length_x", 1000), hint="Side Lenght X", persistent_hint=True)
                    vuetify.VTextField(v_model=("side_length_y", 1000), hint="Side Lenght Y", persistent_hint=True)
                    vuetify.VTextField(v_model=("side_length_z", 1000), hint="Side Lenght Z", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_spherical_mesh":
                    vuetify.VTextField(v_model=("diameter", 1000), hint="Diameter", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_cable_mesh":
                    vuetify.VTextField(v_model=("cable_length", 1000), hint="Cable Length", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_rabbit_mesh" or state.domain_matrix_main_function_selected  == "initialize_grid_with_benchmark_mesh":
                    vuetify.VTextField(v_model=("maximum_discretization", 1000), hint="Maximum discretization (optional)", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_fibrotic_mesh":
                    vuetify.VTextField(v_model=("seed", 1000), hint="Seed (optional)", persistent_hint=True)
                    vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_source_sink_fibrotic_mesh":
                    vuetify.VTextField(v_model=("channel_width", 1000), hint="Channel width", persistent_hint=True)
                    vuetify.VTextField(v_model=("channel_length", 1000), hint="Channel length", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh":
                    vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
                    vuetify.VTextField(v_model=("plain_center", 1000), hint="plain_center", persistent_hint=True)
                    vuetify.VTextField(v_model=("sphere_radius", 1000), hint="Sphere radius", persistent_hint=True)
                    vuetify.VTextField(v_model=("border_zone_radius", 1000), hint="Border Zone Radius", persistent_hint=True)
                    vuetify.VTextField(v_model=("seed", 1000), hint="Seed (optional)", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_cuboid_and_sphere_fibrotic_mesh":
                    vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
                    vuetify.VTextField(v_model=("sphere_center", 1000), hint="sphere_center (optional)", persistent_hint=True)
                    vuetify.VTextField(v_model=("sphere_radius", 1000), hint="Sphere radius", persistent_hint=True)
                    vuetify.VTextField(v_model=("seed", 1000), hint="Seed (optional)", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh_without_inactivating":
                    vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
                    vuetify.VTextField(v_model=("plain_center", 1000), hint="plain_center", persistent_hint=True)
                    vuetify.VTextField(v_model=("border_zone_radius", 1000), hint="Border Zone Radius", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh_and_fibrotic_region":
                    vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
                    vuetify.VTextField(v_model=("seed", 1000), hint="Seed (optional)", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_min_x", 1000), hint="region_min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_max_x", 1000), hint="region_max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_min_y", 1000), hint="region_min_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_max_y", 1000), hint="region_max_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_min_z", 1000), hint="region_min_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_max_z", 1000), hint="region_max_z", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh_and_source_sink_fibrotic_region":
                    vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
                    vuetify.VTextField(v_model=("seed", 1000), hint="Seed (optional)", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_min_x", 1000), hint="region_min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_max_x", 1000), hint="region_max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_min_y", 1000), hint="region_min_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_max_y", 1000), hint="region_max_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_min_z", 1000), hint="region_min_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("region_max_z", 1000), hint="region_max_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("source_sink_min_x", 1000), hint="source_sink_min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("source_sink_max_x", 1000), hint="source_sink_max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("side_length", 1000), hint="side_length", persistent_hint=True)
                if state.domain_matrix_main_function_selected == "initialize_grid_with_square_mesh":
                    vuetify.VTextField(v_model=("side_length", 1000), hint="side_length", persistent_hint=True)


                with vuetify.VList(classes="pt-5"):
                    vuetify.VSubheader("Cellular model")
                
                #ode_solver
                vuetify.VSelect(
                    items=("library_file_options", library_file_options),
                    label="Model",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-5",
                    v_model=("library_file_select", "opção3"),
                ) 

            with vuetify.VList(classes="pt-5"):
                    vuetify.VSubheader("Stimuli")
            for i in range(int(state.n_estimulos)):
                with vuetify.VList(classes="pt-5"):
                    vuetify.VSubheader("Stim" + str(i))
                vuetify.VTextField(v_model=("start_stim_"+str(i), 1000), hint="Start Stim", persistent_hint=True)
                vuetify.VTextField(v_model=("duration_"+str(i), 1000), hint="Duration", persistent_hint=True)
                vuetify.VTextField(v_model=("current_"+str(i), 1000), hint="Current", persistent_hint=True)
                
                vuetify.VSelect(
                    label="Stimuli main function",
                    v_model=("stimuli_main_function_selected"+str(i), "stim_if_x_less_than"),
                    items=("stimuli_main_function_options", stimuli_main_function_options),
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="pt-5",
                ) 

                if state["stimuli_main_function_selected"+str(i)] == "stim_if_x_less_than":
                    vuetify.VTextField(v_model=("x_limit"+str(i), 1000), hint="x_limit", persistent_hint=True)                    
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_y_less_than":
                    vuetify.VTextField(v_model=("y_limit"+str(i), 1000), hint="y_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_z_less_than":
                    vuetify.VTextField(v_model=("z_limit"+str(i), 1000), hint="z_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_x_greater_equal_than":
                    vuetify.VTextField(v_model=("x_limit"+str(i), 1000), hint="x_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_y_greater_equal_than":
                    vuetify.VTextField(v_model=("y_limit"+str(i), 1000), hint="y_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_z_greater_equal_than":
                    vuetify.VTextField(v_model=("z_limit"+str(i), 1000), hint="z_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_sphere":
                    vuetify.VTextField(v_model=("center_x"+str(i), 1000), hint="center_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_y"+str(i), 1000), hint="center_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_z"+str(i), 1000), hint="center_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("radius"+str(i), 1000), hint="radius", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_x_y_limits":
                    vuetify.VTextField(v_model=("max_x"+str(i), 1000), hint="max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x"+str(i), 1000), hint="min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y"+str(i), 1000), hint="max_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y"+str(i), 1000), hint="min_y", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_x_y_z_limits":
                    vuetify.VTextField(v_model=("max_x"+str(i), 1000), hint="max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x"+str(i), 1000), hint="min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y"+str(i), 1000), hint="max_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y"+str(i), 1000), hint="min_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_z"+str(i), 1000), hint="max_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_z"+str(i), 1000), hint="min_z", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_inside_circle_than":
                    vuetify.VTextField(v_model=("center_x"+str(i), 1000), hint="center_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_y"+str(i), 1000), hint="center_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_z"+str(i), 1000), hint="center_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("radius"+str(i), 1000), hint="radius", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_id_less_than":
                    vuetify.VTextField(v_model=("id_limit"+str(i), 1000), hint="id_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_if_id_greater_than":
                    vuetify.VTextField(v_model=("id_limit"+str(i), 1000), hint="id_limit", persistent_hint=True)
                if state["stimuli_main_function_selected"+str(i)] == "stim_concave":
                    vuetify.VTextField(v_model=("max_x_1"+str(i), 1000), hint="max_x_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x_1"+str(i), 1000), hint="min_x_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y_1"+str(i), 1000), hint="max_y_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y_1"+str(i), 1000), hint="min_y_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_x_2"+str(i), 1000), hint="max_x_2", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x_2"+str(i), 1000), hint="min_x_2", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y_2"+str(i), 1000), hint="max_y_2", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y_2"+str(i), 1000), hint="min_y_2", persistent_hint=True)


            with vuetify.VBtn(hint = "Add Stim", click=addstim):
                vuetify.VIcon("mdi-plus")
            with vuetify.VBtn(hint="Remove Stim", click=removestim):
                vuetify.VIcon("mdi-minus")
            with vuetify.VBtn(hint="Clear all stimuli", click=clearstims):
                vuetify.VIcon("mdi-delete")

            with vuetify.VCol(style="max-width: 33%", align ="start", cols=4, sm=4):
                vuetify.VBtn("Run", click=runMonoAlg3D)

        with layout.toolbar as tb: 

            #Barra de carregamento abaixo do header
            vuetify.VProgressLinear(
                indeterminate=True,
                absolute=True,
                bottom=True,
                active=("trame__busy",),
            )

            #Estava tentando colocar um icone, mas não consigo.
            #https://vuetifyjs.com/en/api/v-btn/#props


            vuetify.VDivider(vertical=True, classes="mx-5")

            vuetify.VTextField(
                v_model=("printRate", 10), 
                hint="Print Rate", 
                persistent_hint=True,
                )
            
            #style="position: absolute; top: 10px; left: 25px; width: 600px;",
            #classes="fill-height",

            """ SE FOR VOLTAR A USAR SLIDER 
            vuetify.VSlider(
                v_model=("nome", funcao),
                min=3,
                max=60,
                step=1,
                hide_details=True,
                dense=True,
                style="max-width: 300px",
            ) """

            vuetify.VDivider(vertical=True, classes="mx-5")
            
            with vuetify.VBtn(icon=True, click=firstTime):
                vuetify.VIcon("mdi-page-first")

            with vuetify.VBtn(icon=True, click=subTime):
                vuetify.VIcon("mdi-chevron-left")
            
            #não consegui diminuir a largura dele
            vuetify.VTextField(v_model=("time_value", 0), change=update_frame, number = True, hint="Real Time (ms)", persistent_hint=True, style="width: 5px; height: 100%") #Esse style não funciona no texto, mas funciona em outros elementos 
            
            with vuetify.VBtn(icon=True, click=addTime):
                vuetify.VIcon("mdi-chevron-right")

            with vuetify.VBtn(
                icon=True,
                click=playAnimation,):
                vuetify.VIcon("mdi-play")

            with vuetify.VBtn(icon=True, click=lastTime):
                vuetify.VIcon("mdi-page-last")

            """ with vuetify.VBtn(icon=True, click=addClip):
                vuetify.VIcon("mdi-angle-acute") """
        
        #Isso é a parte inferior e maior da página (onde tudo é plotado por enquanto)
        with layout.content:
            with vuetify.VContainer(fluid=True,classes="pa-0 fill-height"):
                global html_view
                html_view = paraview.VtkRemoteLocalView(view,namespace="demo")
                """ with vuetify.VCol(style="max-width: 50%",classes="ma-0 fill-height", align ="start", cols=6, sm=6):
                    x = [i for i in range(100)]
                    y = [x[i]**2 for i in range(100)]
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='x²'))

                    fig.update_layout(
                        title='Gráfico de x²',
                        xaxis_title='x',
                        yaxis_title='x²',
                    )

                    plot_view = plotly.Figure(fig)
                    plot_view.update(fig) """

update_domain_params()

#Chama função de carregar dados quando o servidor inicia
ctrl.on_server_ready.add(load_data)

#Inicia o servidor
server.start()



""" Como corrigir o colormap:

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# get display properties
simulation_resultpvdDisplay = GetDisplayProperties(simulation_resultpvd, view=renderView1)

# rescale color and/or opacity maps used to exactly fit the current data range
simulation_resultpvdDisplay.RescaleTransferFunctionToDataRange(False, True)

# get color transfer function/color map for 'Scalars_'
scalars_LUT = GetColorTransferFunction('Scalars_')

# get opacity transfer function/opacity map for 'Scalars_'
scalars_PWF = GetOpacityTransferFunction('Scalars_')

# get 2D transfer function for 'Scalars_'
scalars_TF2D = GetTransferFunction2D('Scalars_')

# rescale color and/or opacity maps used to exactly fit the current data range
simulation_resultpvdDisplay.RescaleTransferFunctionToDataRange(False, True)
 """