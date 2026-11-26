from collections import deque
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Senha:
    codigo: str
    especialidade: str
    categoria: str  # "Normal" ou "Preferencial"
    prioridade: int  # 1 = Preferencial, 2 = Normal
    ordem_chegada: int


class FilaFIFO:
    """Estrutura de Fila FIFO (First In, First Out) para pacientes Normais."""
    def __init__(self):
        self._itens = deque()

    def enfileirar(self, senha: Senha) -> None:
        self._itens.append(senha)

    def desenfileirar(self) -> Optional[Senha]:
        if self.esta_vazia():
            return None
        return self._itens.popleft()

    def esta_vazia(self) -> bool:
        return len(self._itens) == 0

    def tamanho(self) -> int:
        return len(self._itens)

    def listar(self) -> List[Senha]:
        return list(self._itens)


class ArvorePrioridade:
    """
    Árvore Binária de Prioridade (Min-Heap) representada em vetor.
    Critério de ordenação: (prioridade, ordem_chegada), garantindo que
    pacientes preferenciais sejam atendidos primeiro e em ordem FIFO.
    """
    def __init__(self):
        self._nos: List[Senha] = []

    def _chave(self, senha: Senha) -> tuple:
        return (senha.prioridade, senha.ordem_chegada)

    def inserir(self, senha: Senha) -> None:
        self._nos.append(senha)
        self._subir(len(self._nos) - 1)

    def remover_topo(self) -> Optional[Senha]:
        if self.esta_vazia():
            return None
        if len(self._nos) == 1:
            return self._nos.pop()

        raiz = self._nos[0]
        self._nos[0] = self._nos.pop()
        self._descer(0)
        return raiz

    def _subir(self, indice: int) -> None:
        while indice > 0:
            pai = (indice - 1) // 2
            if self._chave(self._nos[indice]) < self._chave(self._nos[pai]):
                self._nos[indice], self._nos[pai] = self._nos[pai], self._nos[indice]
                indice = pai
            else:
                break

    def _descer(self, indice: int) -> None:
        total = len(self._nos)
        while True:
            menor = indice
            esq = 2 * indice + 1
            dir_ = 2 * indice + 2

            if esq < total and self._chave(self._nos[esq]) < self._chave(self._nos[menor]):
                menor = esq
            if dir_ < total and self._chave(self._nos[dir_]) < self._chave(self._nos[menor]):
                menor = dir_

            if menor != indice:
                self._nos[indice], self._nos[menor] = self._nos[menor], self._nos[indice]
                indice = menor
            else:
                break

    def esta_vazia(self) -> bool:
        return len(self._nos) == 0

    def tamanho(self) -> int:
        return len(self._nos)

    def listar_ordenado(self) -> List[Senha]:
        return sorted(self._nos, key=self._chave)


class GerenciadorFilaEspecialidade:
    """Gerencia a Árvore de Prioridade (Preferenciais) e a Fila FIFO (Normais) de uma especialidade."""
    def __init__(self, sigla: str, nome: str):
        self.sigla = sigla
        self.nome = nome
        self.arvore_preferencial = ArvorePrioridade()
        self.fila_normal = FilaFIFO()
        self.contador_normal = 0
        self.contador_preferencial = 0
        self.contador_chegada = 0
        self.ultima_chamada: Optional[Senha] = None

    def emitir_senha(self, categoria: str) -> Senha:
        cat = categoria.strip().capitalize()
        self.contador_chegada += 1

        if cat == "Preferencial":
            self.contador_preferencial += 1
            codigo = f"{self.sigla}-P{self.contador_preferencial:03d}"
            senha = Senha(codigo, self.nome, "Preferencial", 1, self.contador_chegada)
            self.arvore_preferencial.inserir(senha)
            return senha

        elif cat == "Normal":
            self.contador_normal += 1
            codigo = f"{self.sigla}-N{self.contador_normal:03d}"
            senha = Senha(codigo, self.nome, "Normal", 2, self.contador_chegada)
            self.fila_normal.enfileirar(senha)
            return senha

        else:
            raise ValueError("Categoria inválida. Escolha 'Normal' ou 'Preferencial'.")

    def chamar_proxima(self) -> Optional[Senha]:
        if not self.arvore_preferencial.esta_vazia():
            chamada = self.arvore_preferencial.remover_topo()
        elif not self.fila_normal.esta_vazia():
            chamada = self.fila_normal.desenfileirar()
        else:
            return None

        self.ultima_chamada = chamada
        return chamada

    def ordem_atendimento(self) -> List[Senha]:
        return self.arvore_preferencial.listar_ordenado() + self.fila_normal.listar()

    def total_aguardando(self) -> int:
        return self.arvore_preferencial.tamanho() + self.fila_normal.tamanho()
