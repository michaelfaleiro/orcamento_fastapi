
from fastapi import APIRouter, Form, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from app.database import db
from app.extensions.convert_objectId import convert_objectid
from app.services.pdf_generator import gerar_pdf
from fastapi.responses import StreamingResponse
from io import BytesIO
from bson import ObjectId
from typing import List
from datetime import datetime

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


# Rota Index
@router.get("/", response_class=HTMLResponse) 
async def home(request: Request, placa: str = Query(default=None)):
    orcamentos = []

    if placa:
        filtro = {"placa": {"$regex": placa, "$options": "i"}}
        async for orcamento in db["orcamentos"].find(filtro).sort("_id", -1):
            convert_objectid(orcamento)
            orcamentos.append(orcamento)
    else:
        async for orcamento in db["orcamentos"].find().sort("_id", -1).limit(10):
            convert_objectid(orcamento)
            orcamentos.append(orcamento)
        
    return templates.TemplateResponse("index.html", {"request": request, "orcamentos": orcamentos, "filtro": placa or ""})


# Rota Orçamento por id    
@router.get("/orcamento/{id}/", response_class=HTMLResponse)
async def orcamento(request: Request, id: str):
    orcamento = await db["orcamentos"].find_one({"_id": ObjectId(id)})
    convert_objectid(orcamento)
    total = sum([produto["quantidade"] * produto["preco_unitario"] for produto in orcamento["produtos"]])
    return templates.TemplateResponse("orcamento.html", {"request": request, "orcamento": orcamento, "total": total})


# Novo Orçamento
@router.post("/orcamento/novo", response_class=HTMLResponse)
async def create_orcamento(request: Request, veiculo: str = Form(...), placa: str = Form(...)):
    
    if not veiculo or not placa:
        print("Veículo e Placa são obrigatórios")
        return templates.TemplateResponse("index.html", {"request": request, "error": "Veículo e Placa são obrigatórios"})

    orcamento = {
        "veiculo": veiculo,
        "placa": placa,
        "produtos": [],
        "data_criacao": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "status": "novo"
    }
    result = await db["orcamentos"].insert_one(orcamento)
    return RedirectResponse(url=f"/orcamento/{str(result.inserted_id)}/", status_code=303)
                           
# Adicionar Produto
@router.post("/orcamento/{id}/produto/novo", response_class=HTMLResponse)
async def add_produto(id: str, nome: str = Form(...), quantidade: int = Form(...), preco_unitario: str = Form(...)):
    orcamento = await db["orcamentos"].find_one({"_id": ObjectId(id)})
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
            
    orcamento["produtos"].append({
        "_id": ObjectId(),
        "nome": nome,
        "quantidade": quantidade,
        "preco_unitario": float(preco_unitario.replace(",", "."))
    })
    await db["orcamentos"].update_one({"_id": ObjectId(id)}, {"$set": orcamento})
    return RedirectResponse(url=f"/orcamento/{id}/", status_code=303)

# Remover Produto
@router.get("/orcamento/{id}/produto/{produto_id}/remover/", response_class=HTMLResponse)
async def remove_produto(id: str, produto_id: str):
    orcamento = await db["orcamentos"].find_one({"_id": ObjectId(id)})
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    orcamento["produtos"] = [produto for produto in orcamento["produtos"] if produto["_id"] != ObjectId(produto_id)]
    
    await db["orcamentos"].update_one({"_id": ObjectId(id)}, {"$set": orcamento})
    return RedirectResponse(url=f"/orcamento/{id}/", status_code=303)

# Editar Produto
@router.post("/orcamento/{id}/produto/{produto_id}/editar/", response_class=HTMLResponse)
async def edit_produto(id: str, produto_id: str, nome: str = Form(...), quantidade: int = Form(...), preco_unitario: str = Form(...)):
    orcamento = await db["orcamentos"].find_one({"_id": ObjectId(id)})
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    for produto in orcamento["produtos"]:
        if produto["_id"] == ObjectId(produto_id):
            produto["nome"] = nome
            produto["quantidade"] = quantidade
            produto["preco_unitario"] = float(preco_unitario.replace(",", "."))
            break
    
    await db["orcamentos"].update_one({"_id": ObjectId(id)}, {"$set": orcamento})
    return RedirectResponse(url=f"/orcamento/{id}/", status_code=303)

# Alterar Status
@router.post("/orcamento/{orcamento_id}/status")
async def atualizar_status(orcamento_id: str, status: str = Form(...)):
    result = await db["orcamentos"].update_one({"_id": ObjectId(orcamento_id)}, {"$set": {"status": status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return RedirectResponse(url=f"/orcamento/{orcamento_id}/", status_code=303)

# Gerar Pdf
@router.post('/orcamentos/{orcamento_id}/pdf', response_class=HTMLResponse)
async def orcamento_pdf(orcamento_id: str, veiculo: str = Form(...), placa: str = Form(...),
                         produtos_nome: List[str] = Form(...), produtos_quantidade: List[int] = Form(...), 
                         produtos_preco_unitario: List[float] = Form(...)):
    produtos = []
    for nome, quantidade, preco_unitario in zip(produtos_nome, produtos_quantidade, produtos_preco_unitario):
        produtos.append({
            "nome": nome,
            "quantidade": quantidade,
            "preco_unitario": preco_unitario
        })

    orcamento = {
        "veiculo": veiculo,
        "placa": placa,
        "_id": orcamento_id,
        "produtos": produtos
    }

    pdf_content = gerar_pdf(orcamento)
    buffer = BytesIO(pdf_content)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=orcamento.pdf"})