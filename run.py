import os
import subprocess

# Parâmetros fixos
active_size = 4
passive_size = 6
fail_std = 0.1
max_cycles = 30
debug_nodes = ["0", "1", "9"]
script = "sc_v11.py"

# Caminho absoluto do script raiz
script_path = os.path.abspath(script)

# Listas de variação
total_nodes_list = range(10, 51, 10)       # 10,20,30,40,50
fail_probs = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55] # 10 pontos eixo x

# Número de execuções por configuração
repetitions = 30

for n in total_nodes_list:
    n_dir = f"n{n}"
    os.makedirs(n_dir, exist_ok=True)

    for p in fail_probs:
        prob_str = f"prob{str(p).replace('.', '_')}"
        prob_dir = os.path.join(n_dir, prob_str)
        os.makedirs(prob_dir, exist_ok=True)

        for rep in range(1, repetitions + 1):
            run_dir = os.path.join(prob_dir, f"rep{rep}")
            os.makedirs(run_dir, exist_ok=True)

            # Arquivos de saída (relativos ao run_dir)
            csv_file = "res.csv"
            debug_file = os.path.join(run_dir, "debug.txt")

            # Monta o comando
            cmd = [
                "python3", script_path,
                "--total_nodes", str(n),
                "--active_size", str(active_size),
                "--passive_size", str(passive_size),
                "--fail_mean", str(p),
                "--fail_std", str(fail_std),
                "--max_cycles", str(max_cycles),
                "--debug_nodes"
            ] + debug_nodes + [
                "--csv_filename", csv_file,
                "--save_graphs"
            ]

            print(f"\nExecutando em {run_dir}: {cmd}")
            with open(debug_file, "w") as dbg:
                subprocess.run(cmd, stdout=dbg, stderr=subprocess.STDOUT, cwd=run_dir)
