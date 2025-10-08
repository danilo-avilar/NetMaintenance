import random
import csv
import matplotlib.pyplot as plt
import argparse
import os

class Node:
    def __init__(self, node_id, active_size, passive_size, total_nodes):
        self.id = node_id
        self.total_nodes = total_nodes
        self.active_size = active_size
        self.passive_size = passive_size
        self.active = set()
        self.passive = set()
        self.passive_history = set()

    def initialize_neighbors(self):
        others = list(set(range(self.total_nodes)) - {self.id})
        random.shuffle(others)
        self.active = set(others[:self.active_size])
        self.passive = set(others[self.active_size:self.active_size + self.passive_size])
        self.passive_history.update(self.passive)

    def ping_cycle(self, params):
        responded = set()
        failed = set()
        message_count = 0
        for neighbor in list(self.active):
            message_count += 1
            fail_prob = sample_fail_prob(params)
            if random.random() < fail_prob:
                failed.add(neighbor)
            else:
                responded.add(neighbor)
        return responded, failed, message_count

    def replace_failed(self, failed, params):
        replacements_log = []
        test_messages = 0
        to_process = []
        for f in failed:
            if f in self.active:
                self.active.remove(f)
                to_process.append(f)
        for f in to_process:
            replaced = False
            while len(self.active) < self.active_size and self.passive:
                candidate = random.choice(list(self.passive))
                self.passive.remove(candidate)
                test_messages += 1
                fail_prob = sample_fail_prob(params)
                if random.random() >= fail_prob:
                    self.active.add(candidate)
                    replacements_log.append((f, candidate, "PING OK"))
                    replaced = True
                    break
                else:
                    replacements_log.append((f, candidate, "PING FAIL"))
            if not replaced and len(self.active) < self.active_size:
                replacements_log.append((f, None, "SEM CANDIDATO"))
        self._replenish_passive()
        return replacements_log, test_messages

    def shuffle_passive(self, nodes):
        if not self.active:
            return
        partner_id = random.choice(list(self.active))
        partner = nodes[partner_id]
        swap_count = max(1, int(self.passive_size * 0.3))
        my_swap = random.sample(self.passive, min(swap_count, len(self.passive)))
        partner_swap = random.sample(partner.passive, min(swap_count, len(partner.passive)))
        for p in my_swap:
            self.passive.remove(p)
        for p in partner_swap:
            partner.passive.remove(p)
        self.passive.update([p for p in partner_swap if p != self.id and p not in self.active])
        partner.passive.update([p for p in my_swap if p != partner.id and p not in partner.active])
        self._replenish_passive()
        partner._replenish_passive()
        self.passive_history.update(self.passive)
        partner.passive_history.update(partner.passive)

    def _replenish_passive(self):
        needed = self.passive_size - len(self.passive)
        if needed > 0:
            candidates = set(range(self.total_nodes)) - {self.id} - self.active - self.passive
            if candidates:
                new_peers = random.sample(list(candidates), min(needed, len(candidates)))
                self.passive.update(new_peers)
                self.passive_history.update(new_peers)

def sample_fail_prob(params):
    """Sorteia probabilidade de falha a partir de uma gaussiana"""
    p = random.gauss(params.fail_mean, params.fail_std)
    return min(1.0, max(0.0, p))  # garante que fique entre 0 e 1

def simulate_with_debug(params):
    random.seed()
    nodes = [Node(i, params.active_size, params.passive_size, params.total_nodes) for i in range(params.total_nodes)]
    for node in nodes:
        node.initialize_neighbors()

    avg_active_list = []
    avg_passive_diversity_list = []
    messages_per_cycle = []
    total_messages = 0
    convergence_cycle = None
    csv_rows = []
    messages_per_node_cumulative = [0] * params.total_nodes
    messages_per_node_evolution = [[] for _ in range(params.total_nodes)]

    for cycle in range(params.max_cycles):
        print(f"\n=== CICLO {cycle} ===")
        ping_results = {}
        promotion_info = {}
        cycle_messages = 0
        cycle_messages_per_node = {}

        # Debug: listas iniciais
        for node in nodes:
            if node.id in params.debug_nodes:
                print(f"\nNó {node.id} - Ativos iniciais: {sorted(node.active)} | Passivos iniciais: {sorted(node.passive)}")

        # Pings
        for node in nodes:
            responded, failed, msg_count = node.ping_cycle(params)
            ping_results[node.id] = (responded, failed, msg_count)
            cycle_messages += msg_count
            cycle_messages_per_node[node.id] = msg_count

        # Debug: resultados de ping
        for node_id in params.debug_nodes:
            if node_id < params.total_nodes:
                responded, failed, msg_count = ping_results[node_id]
                print(f"\nNó {node_id} - Ping OK: {sorted(responded)} | Ping FAIL: {sorted(failed)}")

        # Substituições
        for node in nodes:
            _, failed, _ = ping_results[node.id]
            repl_log, test_msgs = node.replace_failed(failed, params)
            promotion_info[node.id] = (repl_log, test_msgs)
            cycle_messages += test_msgs
            cycle_messages_per_node[node.id] += test_msgs

        # Debug: substituições
        for node_id in params.debug_nodes:
            if node_id < params.total_nodes:
                repl_log, test_msgs = promotion_info[node_id]
                for old, cand, status in repl_log:
                    if cand is None:
                        print(f"Nó {node_id} - Substituindo ativo {old}: {status} (sem candidatos na Passive View)")
                    else:
                        print(f"Nó {node_id} - Substituindo ativo {old} por passivo {cand} → {status}")

        # Shuffle
        for node in nodes:
            node.shuffle_passive(nodes)

        # Debug: mensagens por nó
        for node_id in params.debug_nodes:
            if node_id < params.total_nodes:
                print(f"Nó {node_id} - Mensagens enviadas no ciclo: {cycle_messages_per_node[node_id]}")

        # Atualiza acumulados por nó
        for node_id, msg_count in cycle_messages_per_node.items():
            messages_per_node_cumulative[node_id] += msg_count
            messages_per_node_evolution[node_id].append(messages_per_node_cumulative[node_id])

        # Métricas
        active_counts = [len(n.active) for n in nodes]
        avg_active = sum(active_counts) / params.total_nodes
        avg_active_list.append(avg_active)
        passive_diversity = [len(n.passive_history) for n in nodes]
        avg_passive_diversity = sum(passive_diversity) / params.total_nodes
        avg_passive_diversity_list.append(avg_passive_diversity)
        if convergence_cycle is None and all(count >= params.active_size for count in active_counts):
            convergence_cycle = cycle

        total_messages += cycle_messages
        messages_per_cycle.append(cycle_messages)

        print(f"\nResumo: Média de ativos = {avg_active:.2f} | Diversidade passiva média = {avg_passive_diversity:.2f} | Mensagens no ciclo = {cycle_messages} | Total acumulado = {total_messages}")

        # Linha do CSV
        row = {
            "Ciclo": cycle,
            "MediaAtivos": avg_active,
            "MediaDiversidadePassiva": avg_passive_diversity,
            "MensagensCiclo": cycle_messages,
            "MensagensAcumuladas": total_messages
        }
        for i, count in enumerate(active_counts):
            row[f"No{i}_Ativos"] = count
            row[f"No{i}_MensagensCiclo"] = cycle_messages_per_node[i]
            row[f"No{i}_MensagensAcumuladas"] = messages_per_node_cumulative[i]
        csv_rows.append(row)

    # CSV principal
    if params.csv_filename:
        fieldnames = list(csv_rows[0].keys())
        with open(params.csv_filename, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"\n📁 Resultados salvos em: {params.csv_filename}")

        # CSV separado com mensagens acumuladas finais por nó
        base, ext = os.path.splitext(params.csv_filename)
        csv_acum_filename = f"{base}_acc.csv"
        with open(csv_acum_filename, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["No", "MensagensAcumuladas"])
            for i, total in enumerate(messages_per_node_cumulative):
                writer.writerow([i, total])
        print(f"📁 Mensagens acumuladas por nó salvas em: {csv_acum_filename}")

    # Convergência
    if convergence_cycle is not None:
        print(f"\nTempo de convergência: {convergence_cycle} ciclos")
    else:
        print("\nRede não convergiu totalmente dentro do limite de ciclos.")

    return avg_active_list, avg_passive_diversity_list, [len(n.active) for n in nodes], messages_per_cycle, messages_per_node_evolution, messages_per_node_cumulative


def plot_graphs(params, avg_active_list, avg_passive_diversity_list, final_active_counts, messages_per_cycle, messages_per_node_evolution, messages_per_node_cumulative):
    # Média ativos
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(avg_active_list)), avg_active_list, marker="o", label="Média de ativos")
    plt.axhline(y=params.active_size, color="r", linestyle="--", label="Meta de ativos")
    plt.xlabel("Ciclos"); plt.ylabel("Média de vizinhos ativos"); plt.title("Evolução da média de vizinhos ativos")
    plt.legend(); plt.grid(True);
    if params.save_graphs:
        plt.savefig("grafico_media_ativos.png")
    plt.show(block=False); plt.pause(2); plt.close()

    # Diversidade passiva
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(avg_passive_diversity_list)), avg_passive_diversity_list, marker="s", color="purple",
             label="Diversidade média da Passive View")
    plt.xlabel("Ciclos"); plt.ylabel("Quantidade média de vizinhos únicos"); plt.title("Evolução da diversidade da Passive View")
    plt.legend(); plt.grid(True);
    if params.save_graphs:
        plt.savefig("grafico_diversidade_passiva.png")
    plt.show(block=False); plt.pause(2); plt.close()

    # Distribuição final
    plt.figure(figsize=(7, 4))
    plt.hist(final_active_counts, bins=range(0, params.active_size+2), align='left', rwidth=0.8, color='skyblue', edgecolor='black')
    plt.xlabel("Quantidade de vizinhos ativos"); plt.ylabel("Número de nós"); plt.title("Distribuição final de conectividade")
    plt.grid(axis='y');
    if params.save_graphs:
        plt.savefig("grafico_distribuicao.png")
    plt.show(block=False); plt.pause(2); plt.close()

    # Mensagens por ciclo
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(messages_per_cycle)), messages_per_cycle, marker="d", color="orange", label="Mensagens/ciclo")
    plt.xlabel("Ciclos"); plt.ylabel("Quantidade de mensagens"); plt.title("Mensagens trocadas por ciclo")
    plt.legend(); plt.grid(True);
    if params.save_graphs:
        plt.savefig("grafico_mensagens.png")
    plt.show(block=False); plt.pause(2); plt.close()

    # Novo gráfico: evolução das mensagens acumuladas por nó
    plt.figure(figsize=(10, 5))
    for i in params.debug_nodes:
        if i < len(messages_per_node_evolution):
            plt.plot(range(len(messages_per_node_evolution[i])), messages_per_node_evolution[i], label=f"Nó {i}")
    plt.xlabel("Ciclos")
    plt.ylabel("Mensagens acumuladas")
    plt.title("Evolução das mensagens acumuladas por nó (debug)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    if params.save_graphs:
        plt.savefig("grafico_mensagens_acumuladas_por_no_debug.png", bbox_inches='tight')
    plt.show(block=False)
    plt.pause(2)
    plt.close()

    # Gráfico 6: mensagens acumuladas por nó
    plt.figure(figsize=(10, 5))
    plt.bar(range(params.total_nodes), messages_per_node_cumulative, color="green")
    plt.xlabel("Nó")
    plt.ylabel("Mensagens acumuladas")
    plt.title("Mensagens acumuladas por nó ao final da simulação")
    plt.grid(axis='y')
    if params.save_graphs:
        plt.savefig("grafico_mensagens_acumuladas.png")
    plt.show(block=False)
    plt.pause(2)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de Camada de Conectividade para redes mesh")
    parser.add_argument("--total_nodes", type=int, default=50)
    parser.add_argument("--active_size", type=int, default=4)
    parser.add_argument("--passive_size", type=int, default=6)
    parser.add_argument("--fail_mean", type=float, default=0.3)
    parser.add_argument("--fail_std", type=float, default=0.1)
    parser.add_argument("--max_cycles", type=int, default=30)
    parser.add_argument("--debug_nodes", nargs="+", type=int, default=[0,1,2])
    parser.add_argument("--csv_filename", type=str, default="res.csv")
    parser.add_argument("--save_graphs", action="store_true")

    params = parser.parse_args()

    avg_active_list, avg_passive_diversity_list, final_active_counts, messages_per_cycle, messages_per_node_evolution, messages_per_node_cumulative = simulate_with_debug(params)
    plot_graphs(params, avg_active_list, avg_passive_diversity_list, final_active_counts, messages_per_cycle, messages_per_node_evolution, messages_per_node_cumulative)
