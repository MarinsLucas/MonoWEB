#MonoAlgWeb

MonoAlg_3D é um programa de simulação de funções eletrofisiológicas do coração. O íntuito do MonoAlgWeb é incorporar o MonoAlg_3D na nuvem para que seja possível utilizá-lo a partir de qualquer computador com acesso a internet. 
Além disso, o MonoAlgWeb deve apresentar uma interface de visualização que possibilite análise dos resultados. Para isso, foi implementada uma interface utilizando o Paraview e o Trame no arquivo ./app.py . Para execução do arquivo, são necessárias algumas depêndencias do python, que podem ser instaladas da seguinte forma:

pip install trame trame-vuetify vtk trame-vtk 

Instalar dependências do MonoAlg3D para o Ubuntu:

sudo apt-get install nvidia-cuda-dev nvidia-cuda-toolkit

sudo apt-get install libx11-dev libxcursor-dev libxrandr-dev libxinerama-dev libz-dev libxi-dev libglu1-mesa-dev libglvnd-dev