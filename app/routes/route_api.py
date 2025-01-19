from datetime import datetime
from fastapi import APIRouter, Response, HTTPException
from app.models import Orcamento
from app.database import db
from app.services.pdf_generator import gerar_pdf
from bson import ObjectId
from app.extensions.convert_objectId import convert_objectid

router = APIRouter()

# Criar um orçamento
@router.post("/orcamentos/")
async def criar_orcamento(orcamento: Orcamento):
    data_criacao = datetime.now().strftime("%d-%m-%Y %H:%M")
    orcamento_dict = orcamento.model_dump()
    orcamento_dict["data_criacao"] = data_criacao
    result = await db["orcamentos"].insert_one(orcamento_dict)
    orcamento_dict["_id"] = str(result.inserted_id)
    return orcamento_dict

@router.get("/orcamentos/{orcamento_id}")
async def buscar_orcamento(orcamento_id: str):
    orcamento = await db["orcamentos"].find_one({"_id": ObjectId(orcamento_id)})
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    convert_objectid(orcamento)
    return orcamento

@router.get('/orcamentos/')
async def listar_orcamentos():
    orcamentos = []
    async for orcamento in db["orcamentos"].find():
        convert_objectid(orcamento)
        orcamentos.append(orcamento)
    return orcamentos


@router.put("/orcamentos/{orcamento_id}", response_model=Orcamento)
async def atualizar_orcamento(orcamento_id: str, orcamento: Orcamento):
    orcamento_dict = orcamento.model_dump()
    await db["orcamentos"].update_one({"_id": ObjectId(orcamento_id)}, {"$set": orcamento_dict})
    return {"message": "Orçamento atualizado com sucesso!"}


@router.delete("/orcamentos/{orcamento_id}")
async def deletar_orcamento(orcamento_id: str):
    result = await db["orcamentos"].delete_one({"_id": ObjectId(orcamento_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return {"message": "Orçamento deletado com sucesso!"}

# Gerar um PDF para o orçamento
@router.get("/orcamentos/{orcamento_id}/pdf")
async def gerar_pdf_orcamento(orcamento_id: str):
    orcamento = await db["orcamentos"].find_one({"_id": ObjectId(orcamento_id)})
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    pdf_content = gerar_pdf(orcamento)
    headers = {
        "Content-Disposition": f'inline; filename="orcamento_{orcamento_id}.pdf"'
    }
    return Response(content=pdf_content, media_type="application/pdf", headers=headers)