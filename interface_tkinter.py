import tkinter as tk
from tkinter import ttk, messagebox
from controller import ClinicaController


class SistemaClinicaApp:
    def __init__(self, root: tk.Tk, controller: ClinicaController):
        self.root = root
        self.controller = controller
        self.root.title("Sistema de Senhas - Clínica Médica (ED2)")
        self.root.geometry("880x640")
        self.root.resizable(False, False)

        self._construir_interface()
        self.atualizar_painel()

    def _construir_interface(self):
        header = tk.Frame(self.root, bg="#1e3a5f", pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text="SISTEMA DE GERENCIAMENTO DE SENHAS - CLÍNICA MÉDICA",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#1e3a5f"
        ).pack()

        # 1. Emissão de Senhas
        frame_emissao = ttk.LabelFrame(self.root, text="1. Emissão de Senhas", padding=10)
        frame_emissao.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_emissao, text="Especialidade Médica:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.combo_esp = ttk.Combobox(
            frame_emissao,
            values=self.controller.listar_especialidades(),
            state="readonly",
            width=25,
            font=("Arial", 10)
        )
        self.combo_esp.grid(row=0, column=1, padx=5, pady=5)
        self.combo_esp.current(0)
        self.combo_esp.bind("<<ComboboxSelected>>", lambda e: self.atualizar_painel())

        tk.Button(
            frame_emissao, text="Emitir Senha NORMAL (N)", bg="#2e7d32", fg="white",
            font=("Arial", 10, "bold"), width=24, command=lambda: self.acao_emitir("Normal")
        ).grid(row=0, column=2, padx=8, pady=5)

        tk.Button(
            frame_emissao, text="Emitir Senha PREFERENCIAL (P)", bg="#c62828", fg="white",
            font=("Arial", 10, "bold"), width=26, command=lambda: self.acao_emitir("Preferencial")
        ).grid(row=0, column=3, padx=8, pady=5)

        self.lbl_feedback_emissao = tk.Label(frame_emissao, text="Selecione a especialidade e emita uma senha.", font=("Arial", 10), fg="#333")
        self.lbl_feedback_emissao.grid(row=1, column=0, columnspan=4, pady=5)

        # 2. Painel de Atendimento
        frame_painel = ttk.LabelFrame(self.root, text="2. Painel de Atendimento (Última Senha Chamada)", padding=10)
        frame_painel.pack(fill="x", padx=15, pady=5)

        self.lbl_ultima_senha = tk.Label(frame_painel, text="SENHA: ---", font=("Arial", 22, "bold"), fg="#0d47a1")
        self.lbl_ultima_senha.pack()

        self.lbl_detalhes_chamada = tk.Label(frame_painel, text="Especialidade: ---   |   Categoria: ---", font=("Arial", 11, "bold"))
        self.lbl_detalhes_chamada.pack(pady=4)

        tk.Button(
            frame_painel, text="CHAMAR PRÓXIMA SENHA DA ESPECIALIDADE", bg="#1565c0", fg="white",
            font=("Arial", 11, "bold"), width=42, command=self.acao_chamar
        ).pack(pady=6)

        # 3. Filas e Histórico
        frame_listas = tk.Frame(self.root)
        frame_listas.pack(fill="both", expand=True, padx=15, pady=8)

        frame_espera = ttk.LabelFrame(frame_listas, text="3. Ordem de Atendimento (Árvore de Prioridade + FIFO | 30 min/paciente)", padding=8)
        frame_espera.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.lbl_contadores = tk.Label(frame_espera, text="Aguardando: 0 (0 Preferenciais / 0 Normais)", font=("Arial", 10, "bold"))
        self.lbl_contadores.pack(anchor="w", pady=(0, 5))

        self.lista_espera = tk.Listbox(frame_espera, font=("Consolas", 10), height=14)
        self.lista_espera.pack(fill="both", expand=True)

        frame_hist = ttk.LabelFrame(frame_listas, text="4. Histórico de Atendimentos", padding=8)
        frame_hist.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self.lista_historico = tk.Listbox(frame_hist, font=("Consolas", 10), height=15)
        self.lista_historico.pack(fill="both", expand=True)

    def acao_emitir(self, categoria: str):
        esp = self.combo_esp.get()
        res = self.controller.emitir_senha(esp, categoria)
        if res["sucesso"]:
            self.lbl_feedback_emissao.config(text=res["mensagem"], fg="#1b5e20")
        else:
            messagebox.showerror("Erro de Validação", res["mensagem"])
        self.atualizar_painel()

    def acao_chamar(self):
        esp = self.combo_esp.get()
        res = self.controller.chamar_proxima_senha(esp)
        if res["sucesso"]:
            senha = res["senha"]
            self.lbl_ultima_senha.config(text=f"SENHA: {senha.codigo}")
            self.lbl_detalhes_chamada.config(
                text=f"Especialidade: {senha.especialidade}   |   Categoria: {senha.categoria}"
            )
            self.lista_historico.insert(0, f"{senha.codigo} | {senha.especialidade} ({senha.categoria})")
        else:
            messagebox.showwarning("Fila Vazia", res["mensagem"])
        self.atualizar_painel()

    def atualizar_painel(self):
        esp = self.combo_esp.get()
        dados = self.controller.consultar_painel(esp)
        if not dados["sucesso"]:
            return

        self.lbl_ultima_senha.config(text=f"SENHA: {dados['ultima_chamada']}")
        self.lbl_detalhes_chamada.config(
            text=f"Especialidade: {dados['especialidade']}   |   Categoria: {dados['categoria_ultima']}"
        )
        self.lbl_contadores.config(
            text=f"Total Aguardando: {dados['total_aguardando']}  |  "
                 f"Preferenciais (Árvore): {dados['aguardando_preferencial']}  |  "
                 f"Normais (FIFO): {dados['aguardando_normal']}"
        )

        self.lista_espera.delete(0, tk.END)
        if not dados["relacao_espera"]:
            self.lista_espera.insert(tk.END, "Nenhuma senha aguardando nesta especialidade.")
        else:
            for item in dados["relacao_espera"]:
                self.lista_espera.insert(tk.END, item)
