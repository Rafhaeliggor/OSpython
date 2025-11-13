import random
import textwrap
import os
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional

RR_QUANTUM = 2

@dataclass
class Process:
    pid: int
    name: str
    cpu: int  
    mem: int  
    prio: int  
    state: str = field(default="Pronto")  
    arrival_order: int = field(default=0)  

    def __post_init__(self):
        assert self.cpu >= 0

class OS_Simulator:
    def __init__(self):
        self.next_pid = 1
        self.next_arrival = 1
        self.processes: Dict[int, Process] = {}
        self.ready_queue: Deque[int] = deque()  
        self.blocked: List[int] = []  
        self.finished: List[int] = []
        self.context_switches = 0

    def create_process(self, name: str, cpu=None, mem=None, prio=None):
        if cpu is None:
            cpu = random.randint(1, 10)
        if mem is None:
            mem = random.randint(10, 300)
        if prio is None:
            prio = random.randint(1, 5)
        pid = self.next_pid
        self.next_pid += 1
        arrival = self.next_arrival
        self.next_arrival += 1
        p = Process(pid=pid, name=name, cpu=cpu, mem=mem, prio=prio, state="Pronto", arrival_order=arrival)
        self.processes[pid] = p
        self.ready_queue.append(pid)
        print(f"Processo criado: PID {pid} | {name} | CPU={cpu} | MEM={mem} | PRIO={prio}")
        return pid

    def kill_process(self, pid: int):
        p = self.processes.get(pid)
        if not p:
            print(f"PID {pid} não encontrado.")
            return
        p.state = "Finalizado"
        p.cpu = 0
        if pid in self.ready_queue:
            try:
                self.ready_queue.remove(pid)
            except ValueError:
                pass
        if pid in self.blocked:
            self.blocked.remove(pid)
        if pid not in self.finished:
            self.finished.append(pid)
        print(f"Processo {pid} ({p.name}) encerrado (kill).")

    def block_process(self, pid: int):
        p = self.processes.get(pid)
        if not p:
            print(f"PID {pid} não encontrado.")
            return
        if p.state == "Finalizado":
            print("Processo já finalizado.")
            return
        if p.state == "Bloqueado":
            print("Processo já está bloqueado.")
            return
        if pid in self.ready_queue:
            try:
                self.ready_queue.remove(pid)
            except ValueError:
                pass
        p.state = "Bloqueado"
        self.blocked.append(pid)
        print(f"Processo {pid} ({p.name}) bloqueado.")

    def unblock_process(self, pid: int):
        p = self.processes.get(pid)
        if not p:
            print(f"PID {pid} não encontrado.")
            return
        if p.state != "Bloqueado":
            print("Processo não está bloqueado.")
            return
        self.blocked.remove(pid)
        p.state = "Pronto"
        self.ready_queue.append(pid)
        print(f"→ Processo {pid} ({p.name}) desbloqueado e voltou para Pronto.")

    def list_processes(self):
        header = f"{'PID':<4} | {'Nome':<10} | {'CPU':<3} | {'MEM':<4} | {'PRIO':<4} | {'Estado':<10}"
        print(header)
        print("-" * len(header))
        for pid in sorted(self.processes.keys()):
            p = self.processes[pid]
            print(f"{p.pid:<4} | {p.name:<10} | {p.cpu:<3} | {p.mem:<4} | {p.prio:<4} | {p.state:<10}")

    def _print_cycle_state(self, executing_pid: Optional[int], cycle: int, quantum_remaining: Optional[int]=None):
        print("\n" + "="*40)
        print(f"Ciclo {cycle} - Context switches: {self.context_switches}")
        if executing_pid is None:
            print("-> CPU ociosa neste ciclo (nenhum processo pronto).")
        else:
            p = self.processes[executing_pid]
            qr = f" (quantum_rem={quantum_remaining})" if quantum_remaining is not None else ""
            print(f"-> Executando {p.name} (PID {p.pid}) - CPU restante: {p.cpu}{qr}")
        print("Filas:")
        ready_names = [f"{self.processes[pid].name}(PID{pid},CPU{self.processes[pid].cpu})" for pid in self.ready_queue]
        blocked_names = [f"{self.processes[pid].name}(PID{pid})" for pid in self.blocked]
        finished_names = [f"{self.processes[pid].name}(PID{pid})" for pid in self.finished]
        print("  Pronto:", ", ".join(ready_names) if ready_names else "vazia")
        print("  Bloqueado:", ", ".join(blocked_names) if blocked_names else "vazia")
        print("  Finalizado:", ", ".join(finished_names) if finished_names else "nenhum")
        print("="*40)

    def run_fifo(self):
        print("Iniciando execução: FIFO")
        cycle = 0
        current_pid = None
        while self.ready_queue:
            pid = self.ready_queue.popleft()
            p = self.processes[pid]
            if p.state == "Finalizado":
                continue
            if current_pid != pid:
                self.context_switches += 1
            current_pid = pid
            p.state = "Executando"
            while p.cpu > 0:
                cycle += 1
                p.cpu -= 1
                self._print_cycle_state(pid, cycle)
                if p.cpu == 0:
                    p.state = "Finalizado"
                    self.finished.append(pid)
                    print(f"✓ Processo {pid} finalizado!")
                    break
        print(f"Execução FIFO concluída em {cycle} ciclos. Context switches: {self.context_switches}")

    def run_sjf(self):
        print("Iniciando execução: SJF (Shortest Job First) - não preemptivo")
        cycle = 0
        current_pid = None
        while True:
            ready_pids = [pid for pid in self.ready_queue if self.processes[pid].state != "Finalizado"]
            if not ready_pids:
                break
            pid = min(ready_pids, key=lambda x: (self.processes[x].cpu, self.processes[x].arrival_order))
            try:
                self.ready_queue.remove(pid)
            except ValueError:
                pass
            p = self.processes[pid]
            if p.state == "Finalizado":
                continue
            if current_pid != pid:
                self.context_switches += 1
            current_pid = pid
            p.state = "Executando"
            while p.cpu > 0:
                cycle += 1
                p.cpu -= 1
                self._print_cycle_state(pid, cycle)
                if p.cpu == 0:
                    p.state = "Finalizado"
                    self.finished.append(pid)
                    print(f"✓ Processo {pid} finalizado!")
                    break
        print(f"Execução SJF concluída em {cycle} ciclos. Context switches: {self.context_switches}")

    def run_rr(self, quantum=RR_QUANTUM):
        print(f"Iniciando execução: Round Robin (quantum = {quantum})")
        cycle = 0
        while self.ready_queue:
            pid = self.ready_queue.popleft()
            p = self.processes.get(pid)
            if not p or p.state == "Finalizado":
                continue
            self.context_switches += 1
            p.state = "Executando"
            qrem = quantum
            while qrem > 0 and p.cpu > 0:
                cycle += 1
                p.cpu -= 1
                qrem -= 1
                self._print_cycle_state(pid, cycle, quantum_remaining=qrem)
                if p.cpu == 0:
                    p.state = "Finalizado"
                    self.finished.append(pid)
                    print(f"✓ Processo {pid} finalizado!")
                    break
            if p.cpu > 0:
                p.state = "Pronto"
                self.ready_queue.append(pid)
                print(f"↺ Processo {pid} preemptado (restante {p.cpu}) e volta para final da fila.")
        print(f"Execução RR concluída em {cycle} ciclos. Context switches: {self.context_switches}")

    def run_prio(self):
        print("Iniciando execução: Prioridades (1 = mais alta)")
        cycle = 0
        current_pid = None
        while True:
            ready_pids = [pid for pid in self.ready_queue if self.processes[pid].state != "Finalizado"]
            if not ready_pids:
                break
            pid = min(ready_pids, key=lambda x: (self.processes[x].prio, self.processes[x].arrival_order))
            try:
                self.ready_queue.remove(pid)
            except ValueError:
                pass
            p = self.processes[pid]
            if current_pid != pid:
                self.context_switches += 1
            current_pid = pid
            p.state = "Executando"
            while p.cpu > 0:
                cycle += 1
                p.cpu -= 1
                self._print_cycle_state(pid, cycle)
                if p.cpu == 0:
                    p.state = "Finalizado"
                    self.finished.append(pid)
                    print(f"✓ Processo {pid} finalizado!")
                    break
        print(f"Execução por Prioridade concluída em {cycle} ciclos. Context switches: {self.context_switches}")

    def run(self, algorithm: str):
        self.context_switches = 0
        if algorithm == "fifo":
            self.run_fifo()
        elif algorithm == "sjf":
            self.run_sjf()
        elif algorithm == "rr":
            self.run_rr()
        elif algorithm == "prio":
            self.run_prio()
        else:
            print("Algoritmo desconhecido. Use fifo, sjf, rr ou prio.")

def repl():
    sim = OS_Simulator()
    print(textwrap.dedent("""
    Simulador de Escalonador - comandos disponíveis:
      create <nome>       - cria processo com dados aleatórios
      list                - lista processos
      run <fifo|sjf|rr|prio> - executa escalonador
      block <PID>         - bloqueia processo
      unblock <PID>       - desbloqueia processo
      kill <PID>          - encerra processo
      exit                - sai
    """))
    while True:
        try:
            cmd = input("SO> ").strip()
        except EOFError:
            print()
            break
        if not cmd:
            continue
        parts = cmd.split()
        if parts[0] == "create":
            if len(parts) < 2:
                print("Uso: create <nome>")
                continue
            name = " ".join(parts[1:])
            sim.create_process(name)
        elif parts[0] == "list":
            sim.list_processes()
        elif parts[0] == "run":
            if len(parts) != 2:
                print("Uso: run <fifo|sjf|rr|prio>")
                continue
            alg = parts[1].lower()
            sim.run(alg)
        elif parts[0] == "block":
            if len(parts) != 2 or not parts[1].isdigit():
                print("Uso: block <PID>")
                continue
            sim.block_process(int(parts[1]))
        elif parts[0] == "unblock":
            if len(parts) != 2 or not parts[1].isdigit():
                print("Uso: unblock <PID>")
                continue
            sim.unblock_process(int(parts[1]))
        elif parts[0] == "kill":
            if len(parts) != 2 or not parts[1].isdigit():
                print("Uso: kill <PID>")
                continue
            sim.kill_process(int(parts[1]))
        elif parts[0] == "exit":
            print("Encerrando simulador.")
            break
        elif parts[0] == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
        else:
            print("Comando não reconhecido.")

if __name__ == "__main__":
    repl()
