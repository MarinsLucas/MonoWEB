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
import configparser

import paraview.web.venv
from pathlib import Path
from paraview import simple
from paraview.selection import *

from trame.app import get_server, asynchronous
from trame.widgets import vuetify, paraview, plotly
from trame.ui.vuetify import SinglePageWithDrawerLayout
import subprocess
import plotly.graph_objects as go


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
state, ctrl = server.state, server.controller

animationscene = simple.GetAnimationScene()
timekeeper = animationscene.TimeKeeper
metadata = None
time_values = []
show_graph = False
domain_matrix_main_function_options = ["intialize_grid_with_cuboid_mesh", "initialize_grid_with_spherical_mesh", "initialize_grid_with_square_mesh", "initialize_grid_with_cable_mesh", "initialize_grid_with_rabbit_mesh",
                                       "initialize_grid_with_benchmark_mesh", "initialize_grid_with_plain_fibrotic_mesh", "initialize_grid_with_plain_fibrotic_mesh_from_file", "initialize_grid_with_plain_source_sink_fibrotic_mesh", 
                                       "initialize_grid_with_plain_and_sphere_fibrotic_mesh", "initialize_grid_with_cuboid_and_sphere_fibrotic_mesh", "initialize_grid_with_plain_and_sphere_fibrotic_mesh_without_inactivating", "initialize_grid_with_square_mesh_and_fibrotic_region",
                                        "initialize_grid_with_custom_mesh",  "initialize_grid_with_square_mesh_and_source_sink_fibrotic_region"]

library_file_options = ["shared_libs/libToRORd_dynCl_mixed_endo_mid_epi.so", "shared_libs/libmitchell_shaeffer_2003.so", "shared_libs/libstewart_aslanidi_noble_2009.so", "shared_libs/libten_tusscher_2006.so", "shared_libs/libohara_rudy_endo_2011.so",
                        "shared_libs/libbondarenko_2004.so", "shared_libs/libcourtemanche_ramirez_nattel_1998.so", "shared_libs/libfhn_mod.so", "shared_libs/libMaleckar2008.so", "shared_libs/libMaleckar2009.so", "shared_libs/libToRORd_fkatp_mixed_endo_mid_epi.so",
                        "shared_libs/libToRORd_fkatp_endo.so", "shared_libs/libten_tusscher_3_endo.so", "shared_libs/libten_tusscher_2004_endo.so", "shared_libs/libToRORd_Land_mixed_endo_mid_epi.s" ]

stimuli_main_function_options = ["stim_if_x_less_than", "stim_if_y_less_than", "stim_if_z_less_than", "stim_if_x_greater_equal_than","stim_if_y_greater_equal_than", "stim_if_z_greater_equal_than", "set_benchmark_spatial_stim", "stim_sphere",  "stim_x_y_limits", "stim_x_y_z_limits",
                                 "stim_if_inside_circle_than",  "stim_if_id_less_than", "stim_if_id_greater_than", "stim_concave"]
# Custom Classes for our problem
class CardContainer(vuetify.VCard):
    def __init__(self, **kwargs):
        super().__init__(variant="outlined", **kwargs)
        with self:
            with vuetify.VCardTitle():
                self.header = vuetify.VRow(
                    classes="align-center pa-0 ma-0", style="min-height: 40px;"
                )
            vuetify.VDivider()
            self.content = vuetify.VCardText()

class PlotSelectionOverTime(CardContainer):
    def __init__(self, run=None):
        super().__init__(
            classes="ma-4 flex-sm-grow-1", style="width: calc(100% - 504px);"
        )
        ctrl = self.server.controller

        with self.header as header:
            header.add_child("Plot Selection Over Time")

        with self.content as content:
            content.classes = "d-flex flex-shrink-1 pb-0"
            # classes UI
            _chart =  plotly.Figure(
                style="width: 100%; height: 200px;",
                v_show=("task_active === 'classification' && !input_needed",),
                display_mode_bar=False,
            ) 
            ctrl.classification_chart_update = _chart.update

            # similarity UI
            vuetify.VProgressCircular(
                "{{ Math.round(model_viz_similarity) }} %",
                v_show=("task_active === 'similarity' && !input_needed",),
                size=192,
                width=15,
                color="teal",
                model_value=("model_viz_similarity", 0),
            )

#Variáveis dos estímulos:
stimuli_main_function_selected_dicionary = {}
state.n_estimulos = 0
# Load function, runs every time server starts
def load_data(**kwargs):
    global time_values, representation, reader, show_graph
    reader = simple.PVDReader(FileName="C:/Users/lucas/venv/MonoAlgWeb-trame/MonoAlg3D_C/outputs/temp/simulation_result.pvd")
    reader.CellArrays = ['Scalars_']
    reader.UpdatePipeline()
    representation = simple.Show(reader, view)
    time_values = list(timekeeper.TimestepValues)
    
    state.time_value = time_values[0]
    state.times = len(time_values)-1
    state.time = 0
    state.play = False
    state.animationStep = 10 #default = 1
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
    
    ctrl.view_update_image()

global html_view

@state.change("play")
@asynchronous.task 
async def update_play(**kwargs):
    while state.play:
        with state:
            state.time += int(state.animationStep)
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
    state.time -= int(state.animationStep)
    html_view.update_image()
    pass

def addTime():
    state.time += int(state.animationStep)
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
    pass

def removestim():
    state.n_estimulos -= 1
    if state.n_estimulos < 0: 
        state.n_estimulos = 0
    pass

def clearstims():
    state.n_estimulos = 0
    readini("EX01_plain_mesh_healthy")
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

    simple.Hide(reader, view)
    representation = simple.Show(clip, view)
    html_view.update_image()

def playAnimation():
    if state.play:
        state.play = False
    else:
        state.play = True
def readini(nome_arquivo):
    config = configparser.ConfigParser()
    config.read("./MonoAlg3D_C/example_config/" + str(nome_arquivo))

    state.simulation_time = config["main"]["simulation_time"]
    state.print_rate = config["save_result"]["print_rate"]
    state.sigma_x = config["assembly_matrix"]["sigma_x"]
    state.sigma_y = config["assembly_matrix"]["sigma_y"]
    state.sigma_z = config["assembly_matrix"]["sigma_z"]
    state.domain_name = config["domain"]["name"]
    state.domain_matrix_main_function_selected = config["domain"]["main_function"]
    #read domain variáveis
    if state.domain_matrix_main_function_selected == "intialize_grid_with_cuboid_mesh":
        state.side_length_x = config["domain"]["side_lenght_x"]
        state.side_length_y = config["domain"]["side_lenght_y"]
        state.side_length_z = config["domain"]["side_lenght_z"]
       
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
        
        vuetify.VTextField(v_model=("channel_width", 1000), hint="Channel width", persistent_hint=True)
        vuetify.VTextField(v_model=("channel_length", 1000), hint="Channel length", persistent_hint=True)
    if state.domain_matrix_main_function_selected == "initialize_grid_with_plain_and_sphere_fibrotic_mesh":
        vuetify.VTextField(v_model=("phi", 1000), hint="Fibrosis %", persistent_hint=True)
        vuetify.VTextField(v_model=("plain_center", 1000), hint="plain_center", persistent_hint=True)
        vuetify.VTextField(v_model=("sphere_radius", 1000), hint="Sphere radius", persistent_hint=True)
        vuetify.VTextField(v_model=("border_zone_size", 1000), hint="Border Zone Size", persistent_hint=True)
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


    state.library_file_select = config["ode_solver"]["library_file"]




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

        #ode_solver
        file.write("\n[ode_solver]\ndt=0.02\nuse_gpu=yes\ngpu_id=0\nlibrary_file="+str(state.library_file_select))

        #stim
        
    #saida = subprocess.check_output(monoalg_command, shell=True, universal_newlines=True)
    #print(saida)
    pass
@state.change("domain_matrix_main_function_selected")
def changed_domain_function(domain_matrix_main_function_selected, **kwargs):
    update_domain_params()

@state.change("n_estimulos")
def changed_n_estimulos(n_estimulos, **kwargs):
    update_domain_params()

@state.change("stim_temp")
def change_stim_model(stim_temp, **kwargs):
    update_domain_params()

def update_domain_params():
    with SinglePageWithDrawerLayout(server) as layout:
        with layout.drawer as dw:
            #Main: simulation_time só
            vuetify.VTextField(v_model=("simulation_time", 1000), hint="Simulation time", persistent_hint=True)
            
            #save_result: print_rate
            vuetify.VTextField(v_model=("print_rate", 1000), hint="Save rate", persistent_hint=True)

            #assembly_matrix
            vuetify.VTextField(v_model=("sigma_x", 1000), hint="Sigma X", persistent_hint=True)
            vuetify.VTextField(v_model=("sigma_y", 1000), hint="Sigma Y", persistent_hint=True)
            vuetify.VTextField(v_model=("sigma_z", 1000), hint="Sigma Z", persistent_hint=True)
            
            #domain
            vuetify.VTextField(v_model=("domain_name", 1000), hint="Domain Name", persistent_hint=True)
            vuetify.VSelect(
                label="Domain Main Function",
                v_model=("domain_matrix_main_function_selected", "intialize_grid_with_cuboid_mesh"),
                items=("domain_matrix_main_function_options", domain_matrix_main_function_options)
            )
            vuetify.VTextField(v_model=("start_dx", 1000), hint="Start dx", persistent_hint=True)
            vuetify.VTextField(v_model=("start_dy", 1000), hint="Start dy", persistent_hint=True)
            vuetify.VTextField(v_model=("start_dz", 1000), hint="Start dz", persistent_hint=True)
            if state.domain_matrix_main_function_selected == "intialize_grid_with_cuboid_mesh":
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
                vuetify.VTextField(v_model=("border_zone_size", 1000), hint="Border Zone Size", persistent_hint=True)
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

            #ode_solver
            vuetify.VSelect(
                label="Model",
                v_model=("library_file_select", "opção3"),
                items=("library_file_options", library_file_options)
            )

            #ecg

            for i in range(int(state.n_estimulos)):
                
                vuetify.VTextField(v_model=("start_stim_"+str(i), 1000), hint="Start Stim", persistent_hint=True)
                vuetify.VTextField(v_model=("duration_"+str(i), 1000), hint="Duration", persistent_hint=True)
                vuetify.VTextField(v_model=("current_"+str(i), 1000), hint="Current", persistent_hint=True)
                vuetify.VSelect(
                    label="Stimuli main function",
                    v_model=("stim_temp", "stim_if_x_less_than"),
                    items=("stimuli_main_function_options", stimuli_main_function_options),
                )
                stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] = state.stim_temp
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_x_less_than":
                    vuetify.VTextField(v_model=(stimuli_main_function_selected_dicionary["x_limit"+str(i)], 1000), hint="x_limit", persistent_hint=True)                    
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_y_less_than":
                    vuetify.VTextField(v_model=("y_limit"+str(i), 1000), hint="y_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_z_less_than":
                    vuetify.VTextField(v_model=("z_limit"+str(i), 1000), hint="z_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_x_greater_equal_than":
                    vuetify.VTextField(v_model=("x_limit"+str(i), 1000), hint="x_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_y_greater_equal_than":
                    vuetify.VTextField(v_model=("y_limit"+str(i), 1000), hint="y_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_z_greater_equal_than":
                    vuetify.VTextField(v_model=("z_limit"+str(i), 1000), hint="z_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_sphere":
                    vuetify.VTextField(v_model=("center_x"+str(i), 1000), hint="center_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_y"+str(i), 1000), hint="center_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_z"+str(i), 1000), hint="center_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("radius"+str(i), 1000), hint="radius", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_x_y_limits":
                    vuetify.VTextField(v_model=("max_x"+str(i), 1000), hint="max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x"+str(i), 1000), hint="min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y"+str(i), 1000), hint="max_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y"+str(i), 1000), hint="min_y", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_x_y_z_limits":
                    vuetify.VTextField(v_model=("max_x"+str(i), 1000), hint="max_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x"+str(i), 1000), hint="min_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y"+str(i), 1000), hint="max_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y"+str(i), 1000), hint="min_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_z"+str(i), 1000), hint="max_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_z"+str(i), 1000), hint="min_z", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_inside_circle_than":
                    vuetify.VTextField(v_model=("center_x"+str(i), 1000), hint="center_x", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_y"+str(i), 1000), hint="center_y", persistent_hint=True)
                    vuetify.VTextField(v_model=("center_z"+str(i), 1000), hint="center_z", persistent_hint=True)
                    vuetify.VTextField(v_model=("radius"+str(i), 1000), hint="radius", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_id_less_than":
                    vuetify.VTextField(v_model=("id_limit"+str(i), 1000), hint="id_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_if_id_greater_than":
                    vuetify.VTextField(v_model=("id_limit"+str(i), 1000), hint="id_limit", persistent_hint=True)
                if stimuli_main_function_selected_dicionary["stimuli_main_function_selected_"+str(i)] == "stim_concave":
                    vuetify.VTextField(v_model=("max_x_1"+str(i), 1000), hint="max_x_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x_1"+str(i), 1000), hint="min_x_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y_1"+str(i), 1000), hint="max_y_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y_1"+str(i), 1000), hint="min_y_1", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_x_2"+str(i), 1000), hint="max_x_2", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_x_2"+str(i), 1000), hint="min_x_2", persistent_hint=True)
                    vuetify.VTextField(v_model=("max_y_2"+str(i), 1000), hint="max_y_2", persistent_hint=True)
                    vuetify.VTextField(v_model=("min_y_2"+str(i), 1000), hint="min_y_2", persistent_hint=True)


            #stim
            #start
            #duration
            #current
            #main_function = dropdown
            with vuetify.VCol(style="max-width: 33%", align ="start", cols=4, sm=4):
                vuetify.VBtn("Add Stim", click=addstim)
            with vuetify.VCol(style="max-width: 33%", align ="start", cols=4, sm=4):
                vuetify.VBtn("Remove Stim", click=removestim)
            with vuetify.VCol(style="max-width: 33%", align ="start", cols=4, sm=4):
                vuetify.VBtn("Clear Stim", click=clearstims)

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

            vuetify.VTextField(v_model=("animationStep", 10), hint="Animation Step", style="width= 25px; height: 100%")
            vuetify.VBtn("F", click=firstTime)
            vuetify.VBtn("-",
                        click=subTime,
                        )
            #não consegui diminuir a largura dele
            vuetify.VTextField(v_model=("time_value", 0), change=update_frame, number = True, hint="Real Time (ms)", style="width: 25px; height: 100%") #Esse style não funciona no texto, mas funciona em outros elementos 
            vuetify.VBtn("+",
                        click=addTime) 

            with vuetify.VBtn(
                icon=True,
                click=playAnimation,):
                vuetify.VIcon("mdi-play")

            vuetify.VBtn("L", click=lastTime)

            vuetify.VBtn("Clip", click=addClip)
        
        #Isso é a parte inferior e maior da página (onde tudo é plotado por enquanto)
        with layout.content:
            with vuetify.VContainer(fluid=True,classes="pa-0 fill-height"):
                with vuetify.VCol(style="max-width: 50%",classes="ma-0 fill-height", align ="start", cols=6, sm=6):
                    global html_view
                    html_view = paraview.VtkRemoteLocalView(
                        view,
                        namespace="demo",
                    )
                with vuetify.VCol(style="max-width: 50%",classes="ma-0 fill-height", align ="start", cols=6, sm=6):
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
                    plot_view.update(fig)

update_domain_params()

#Chama função de carregar dados quando o servidor inicia
ctrl.on_server_ready.add(load_data)

#Inicia o servidor
server.start()
