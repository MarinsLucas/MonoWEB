The MonoWEB is an integration between the cardiac electrophysiology simulator MonoAlg3D and a intuitive WEB interface.

# Pre-Requisites
Linux or WSL:
- Nvidia Driver
- CUDA library 
- Paraview 5.12+
- Python 3.10+

# Setting the enviroment:
- Configure a virtual environment with python-virtualenv:
```sh
$ python3 -m pip install --user virtualenv 
$ python3 -m pip virtualenv venv
```
For python3.11+, its necessary to use the sudo privileges to install virtualenv.

- Install the Trame dependencies

```sh
$ source ./venv/bin/activate
$ export PV_VENV=~/venv
$ pip install trame trame-vuetify trame-vtk trame-plotly plotly
```

- Clone this repository inside the /venv/ directory
- Build MonoAlg3D (inside the MonoAlg3D_C directory):

```sh
$ ./build.sh simulator
```

- Run (inside the MonoAlg3D_C directory)
```sh
$ pvpython --force-offscreen-rendering app.py --virtual-env ../../ 
```

- To run the examples for MonoWEB, you can run the python file "run_examples.py" inside the MonoAlg_3D directory with the flags:

  --all       Run every available example
  --1         Run EX01 - healthy tissue
  --2         Run EX02 - healthy tissue arrhythmia
  --3         Run EX03 - ischemic arrhythmia
  --4         Run EX04 - 3D healthy tissue
  --5         Run EX05 - fibrillation
  --6         Run EX06 - S1-S2 fibrosis
  --7         Run EX07 - S1-S2 ischemia
  --8         Run EX08 - S1-S2 isthmus
  --9         Run EX09 - fibrosis+ischemia+long qt syndrome
  --10        Run EX10 - long qt syndrome


```sh
$ python3 run_examples.py --all
```

