from enum import Enum


class ACESSO_CIDADAO_ADMIN(Enum):
    SISTEMAS = "sistemas"
    GRUPOS_E_SERVIDORES = "gruposservidores"


class GRUPO_E_SERVIDOR(Enum):
    SERVIDOR = "Servidor"
    GRUPOS = "Grupos"


class ACOES(Enum):
    ADICIONAR_PAPEL = "1 - ADICIONAR PAPEL"
    REMOVER_PAPEL = "2 - REMOVER PAPEL"
