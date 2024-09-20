from enum import Enum


class ACESSO_CIDADAO_ADMIN(Enum):
    SISTEMAS = "sistemas"
    GRUPOS_E_SERVIDORES = "gruposservidores"


class GRUPO_E_SERVIDOR(Enum):
    SERVIDOR = "Servidor"
    GRUPOS = "Grupos"
