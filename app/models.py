from pydantic import BaseModel
from typing import List, Optional



class Produto(BaseModel):
    _id: str
    nome: str 
    quantidade: int 
    preco_unitario: float 

class Orcamento(BaseModel):
    _id: str
    veiculo: str 
    placa: str 
    produtos: List[Produto]
    status: str 
    data_criacao: Optional[str] = None

