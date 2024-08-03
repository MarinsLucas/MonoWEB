import argparse
import subprocess

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")

def main():
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description="Executa comandos baseados nas flags fornecidas.")
    parser.add_argument('--all', action='store_true', help="Run every available example")
    parser.add_argument(f'--1', action='store_true', help=f"Run EX01 - healthy tissue")
    parser.add_argument(f'--2', action='store_true', help=f"Run EX02 - healthy tissue arrhythmia")
    parser.add_argument(f'--3', action='store_true', help=f"Run EX03 - ischemic arrhythmia")
    parser.add_argument(f'--4', action='store_true', help=f"Run EX04 - 3D healthy tissue")
    parser.add_argument(f'--5', action='store_true', help=f"Run EX05 - fibrillation")
    parser.add_argument(f'--6', action='store_true', help=f"Run EX06 - S1-S2 fibrosis")
    parser.add_argument(f'--7', action='store_true', help=f"Run EX07 - S1-S2 ischemia")
    parser.add_argument(f'--8', action='store_true', help=f"Run EX08 - S1-S2 isthmus")
    parser.add_argument(f'--9', action='store_true', help=f"Run EX09 - fibrosis+ischemia+long qt syndrome")
    parser.add_argument(f'--10', action='store_true', help=f"Run EX10 - long qt syndrome" )

    # Analisa os argumentos
    args = parser.parse_args()

    # Lista de comandos que serão executados para cada flag
    commands = {
        '1': './bin/MonoAlg3D -c example_configs/EX01_plain_mesh_healthy.ini',
        '2': './bin/MonoAlg3D -c example_configs/EX02_plain_mesh_S1S2_protocol.ini',
        '3': './bin/MonoAlg3D -c example_configs/EX03_plain_mesh_with_ischemia.ini',
        '4': './bin/MonoAlg3D -c example_configs/EX04_3dwedge_healthy.ini',
        '5': './bin/MonoAlg3D -c example_configs/EX05_spiral_break_up.ini',
        '6': './bin/MonoAlg3D -c example_configs/EX06_fibrosis.ini',
        '7': './bin/MonoAlg3D -c example_configs/EX07_ischemia.ini',
        '8': './bin/MonoAlg3D -c example_configs/EX08_isthmus.ini',
        '9': './bin/MonoAlg3D -c example_configs/EX09_mixed_conditions.ini',
        '10': './bin/MonoAlg3D -c example_configs/EX10_qt.ini',
    }

    # Executa todos os comandos se --all for especificado
    if args.all:
        for key, command in commands.items():
            execute_command(command)
    else:
        # Executa apenas os comandos cujas flags foram especificadas
        for i in range(1, 11):
            flag = getattr(args, str(i))
            if flag:
                command = commands.get(str(i))
                execute_command(command)

if __name__ == "__main__":
    main()

