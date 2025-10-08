import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# -------------------------------------------------------------
plt.rcParams.update({'font.size': 12})  # fonte maior
root_dir = os.getcwd()
modo_graficos = "separado"  # opções: "junto" ou "separado"

results = []

# -------------------------------------------------------------
# COLETA DE DADOS
# -------------------------------------------------------------
for n_dir in sorted([d for d in os.listdir(root_dir) if d.startswith("n") and os.path.isdir(d)]):
    try:
        total_nodes = int(n_dir[1:])
    except:
        continue

    for prob_dir in sorted(os.listdir(n_dir)):
        prob_path = os.path.join(n_dir, prob_dir)
        if not os.path.isdir(prob_path):
            continue

        try:
            fail_prob = float(prob_dir.replace("prob", "").replace("_", "."))
        except:
            continue

        tempos, convergencias, media_ativos0 = [], [], []

        for rep_dir in sorted(os.listdir(prob_path)):
            run_dir = os.path.join(prob_path, rep_dir)
            if not os.path.isdir(run_dir):
                continue

            debug_path = os.path.join(run_dir, "debug.txt")
            res_path = os.path.join(run_dir, "res.csv")

            tempo_convergencia = None
            convergiu = True
            media_ativos_ciclo0 = None

            # --- debug.txt ---
            if os.path.exists(debug_path):
                with open(debug_path, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    if "Tempo de convergência:" in line:
                        try:
                            tempo_convergencia = int(line.split(":")[1].strip().split()[0])
                        except:
                            pass
                    if "Rede não convergiu" in line:
                        convergiu = False
                        tempo_convergencia = None

            # --- res.csv ---
            if os.path.exists(res_path):
                try:
                    df = pd.read_csv(res_path)
                    col_ciclo = [c for c in df.columns if "ciclo" in c.lower()]
                    col_ativos = [c for c in df.columns if "ativo" in c.lower()]
                    if col_ciclo and col_ativos:
                        row0 = df[df[col_ciclo[0]] == 0]
                        if not row0.empty:
                            media_ativos_ciclo0 = float(row0[col_ativos[0]].iloc[0])
                except:
                    pass

            if tempo_convergencia is not None:
                tempos.append(tempo_convergencia)
            convergencias.append(convergiu)
            if media_ativos_ciclo0 is not None:
                media_ativos0.append(media_ativos_ciclo0)

        results.append({
            "Total_Nodes": total_nodes,
            "Fail_Prob": fail_prob,
            "Convergiu_pct": np.mean(convergencias) * 100,
            "Tempo_Convergencia_medio": np.mean(tempos) if tempos else None,
            "Tempo_Convergencia_std": np.std(tempos) if tempos else None,
            "Media_Ativos_Ciclo0_medio": np.mean(media_ativos0) if media_ativos0 else None,
            "Media_Ativos_Ciclo0_std": np.std(media_ativos0) if media_ativos0 else None
        })

# -------------------------------------------------------------
# DATAFRAME FINAL
# -------------------------------------------------------------
df_results = pd.DataFrame(results)
df_results.sort_values(["Total_Nodes", "Fail_Prob"], inplace=True)

print("\n=== RESULTADOS COLETADOS ===")
print(df_results)
df_results.to_csv("analise_resultados.csv", index=False)

# -------------------------------------------------------------
# FUNÇÃO PARA GERAR GRÁFICOS
# -------------------------------------------------------------
def gerar_graficos(df_results, modo="separado"):
    colors = plt.cm.tab10(np.linspace(0, 1, len(df_results["Total_Nodes"].unique())))

    # ---------------------------------------------------------
    # 1️⃣ ATIVOS NO CICLO 0
    # ---------------------------------------------------------
    if modo == "junto":
        plt.figure(figsize=(8,5))
        for color, n in zip(colors, df_results["Total_Nodes"].unique()):
            subset = df_results[df_results["Total_Nodes"] == n]
            plt.errorbar(
                subset["Fail_Prob"],
                subset["Media_Ativos_Ciclo0_medio"],
                yerr=subset["Media_Ativos_Ciclo0_std"],
                marker="o",
                capsize=5,
                color=color,
                label=f"{n} nós"
            )
        plt.xlabel("Probabilidade de falha")
        plt.ylabel("Média de ativos no ciclo 0")
        plt.title("Ativos no ciclo 0 vs Probabilidade de falha")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.ylim(0, max(5, df_results["Media_Ativos_Ciclo0_medio"].max() + 1))
        plt.tight_layout()
        plt.savefig("ativos_ciclo0.pdf", bbox_inches="tight", dpi=300)
        plt.close()

    else:  # modo separado
        for n in df_results["Total_Nodes"].unique():
            subset = df_results[df_results["Total_Nodes"] == n]
            plt.figure(figsize=(7,5))
            plt.errorbar(
                subset["Fail_Prob"],
                subset["Media_Ativos_Ciclo0_medio"],
                yerr=subset["Media_Ativos_Ciclo0_std"],
                marker="o",
                capsize=5,
                color="blue"
            )
            plt.xlabel("Probabilidade de falha")
            plt.ylabel("Média de ativos no ciclo 0")
            plt.title(f"Ativos no ciclo 0 vs Probabilidade de falha ({n} nós)")
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.ylim(0, max(5, subset["Media_Ativos_Ciclo0_medio"].max() + 1))
            plt.tight_layout()
            plt.savefig(f"ativos_ciclo0_{n}nos.pdf", bbox_inches="tight", dpi=300)
            plt.close()

    # ---------------------------------------------------------
    # 2️⃣ TEMPO DE CONVERGÊNCIA
    # ---------------------------------------------------------
    if modo == "junto":
        plt.figure(figsize=(8,5))
        for color, n in zip(colors, df_results["Total_Nodes"].unique()):
            subset = df_results[df_results["Total_Nodes"] == n]
            plt.errorbar(
                subset["Fail_Prob"],
                subset["Tempo_Convergencia_medio"],
                yerr=subset["Tempo_Convergencia_std"],
                marker="s",
                capsize=5,
                color=color,
                label=f"{n} nós"
            )
        plt.xlabel("Probabilidade de falha")
        plt.ylabel("Tempo médio de convergência (ciclos)")
        plt.title("Tempo de convergência vs Probabilidade de falha")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.7)
        ymax = max(5, df_results["Tempo_Convergencia_medio"].max(skipna=True) + 2)
        plt.ylim(0, ymax)
        plt.tight_layout()
        plt.savefig("tempo_convergencia.pdf", bbox_inches="tight", dpi=300)
        plt.close()

    else:  # modo separado
        for n in df_results["Total_Nodes"].unique():
            subset = df_results[df_results["Total_Nodes"] == n]
            plt.figure(figsize=(7,5))
            plt.errorbar(
                subset["Fail_Prob"],
                subset["Tempo_Convergencia_medio"],
                yerr=subset["Tempo_Convergencia_std"],
                marker="s",
                capsize=5,
                color="green"
            )
            plt.xlabel("Probabilidade de falha")
            plt.ylabel("Tempo médio de convergência (ciclos)")
            plt.title(f"Tempo de convergência vs Probabilidade de falha ({n} nós)")
            plt.grid(True, linestyle="--", alpha=0.7)
            ymax = max(5, subset["Tempo_Convergencia_medio"].max(skipna=True) + 2)
            plt.ylim(0, ymax)
            plt.tight_layout()
            plt.savefig(f"tempo_convergencia_{n}nos.pdf", bbox_inches="tight", dpi=300)
            plt.close()

# -------------------------------------------------------------
# EXECUÇÃO
# -------------------------------------------------------------
gerar_graficos(df_results, modo=modo_graficos)
print(f"\nGráficos gerados no modo: {modo_graficos.upper()}")
