from typing import Dict, Any, List
from estruturas_fila import GerenciadorFilaEspecialidade, Senha


class ClinicaController:
    TEMPO_MEDIO_MINUTOS = 30

    def __init__(self):
        self.especialidades: Dict[str, GerenciadorFilaEspecialidade] = {
            "Clínica Geral": GerenciadorFilaEspecialidade("CG", "Clínica Geral"),
            "Cardiologia": GerenciadorFilaEspecialidade("CA", "Cardiologia"),
            "Ortopedia": GerenciadorFilaEspecialidade("OR", "Ortopedia")
        }
        self.historico_atendimentos: List[Senha] = []

    def listar_especialidades(self) -> List[str]:
        return list(self.especialidades.keys())

    def emitir_senha(self, nome_especialidade: str, categoria: str) -> Dict[str, Any]:
        if nome_especialidade not in self.especialidades:
            return {"sucesso": False, "mensagem": f"Especialidade '{nome_especialidade}' inválida."}

        try:
            gerenciador = self.especialidades[nome_especialidade]
            nova_senha = gerenciador.emitir_senha(categoria)
            pos = gerenciador.ordem_atendimento().index(nova_senha)
            tempo_estimado = pos * self.TEMPO_MEDIO_MINUTOS
            return {
                "sucesso": True,
                "senha": nova_senha,
                "tempo_estimado": tempo_estimado,
                "mensagem": (
                    f"Senha {nova_senha.codigo} ({nova_senha.categoria} - {nova_senha.especialidade}) emitida | "
                    f"Pacientes à frente: {pos} | Espera estimada: {tempo_estimado} min."
                )
            }
        except ValueError as erro:
            return {"sucesso": False, "mensagem": str(erro)}

    def chamar_proxima_senha(self, nome_especialidade: str) -> Dict[str, Any]:
        if nome_especialidade not in self.especialidades:
            return {"sucesso": False, "mensagem": f"Especialidade '{nome_especialidade}' inválida."}

        gerenciador = self.especialidades[nome_especialidade]
        chamada = gerenciador.chamar_proxima()

        if chamada is None:
            return {
                "sucesso": False,
                "fila_vazia": True,
                "mensagem": f"Aviso: Não há pacientes aguardando na fila de {nome_especialidade}."
            }

        self.historico_atendimentos.append(chamada)
        return {
            "sucesso": True,
            "fila_vazia": False,
            "senha": chamada,
            "mensagem": f"Senha {chamada.codigo} ({chamada.categoria}) chamada para {chamada.especialidade}."
        }

    def consultar_painel(self, nome_especialidade: str) -> Dict[str, Any]:
        if nome_especialidade not in self.especialidades:
            return {"sucesso": False, "mensagem": "Especialidade inválida."}

        g = self.especialidades[nome_especialidade]
        ordem = g.ordem_atendimento()
        relacao_espera = [
            f"{idx + 1}º: {s.codigo} ({s.categoria}) — Espera estimada: {idx * self.TEMPO_MEDIO_MINUTOS} min"
            for idx, s in enumerate(ordem)
        ]

        return {
            "sucesso": True,
            "especialidade": g.nome,
            "ultima_chamada": g.ultima_chamada.codigo if g.ultima_chamada else "Nenhuma",
            "categoria_ultima": g.ultima_chamada.categoria if g.ultima_chamada else "---",
            "total_aguardando": g.total_aguardando(),
            "aguardando_preferencial": g.arvore_preferencial.tamanho(),
            "aguardando_normal": g.fila_normal.tamanho(),
            "relacao_espera": relacao_espera
        }
