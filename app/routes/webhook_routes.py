from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from app.controllers.webhook_controller import handle_get_webhook, handle_post_webhook, handle_get_professions, handle_post_ciudadano, handle_post_recuperar_pin_ciudadano

#from bson import ObjectId

from app.config import templates
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "AMI 0.0.2"})

@router.api_route("/webhook", methods=["GET", "POST"])
async def webhook(request: Request):
    if request.method == "GET":
        return await handle_get_webhook(request)
    elif request.method == "POST":
        return await handle_post_webhook(request)

@router.get("/profesiones", response_class=JSONResponse)
async def profesiones(request: Request):
    return await handle_get_professions(request)

@router.post("/ciudadano", response_class=JSONResponse)
async def ciudadano(request: Request):
    return await handle_post_ciudadano(request)

@router.post("/rec_pin_ciudadano", response_class=JSONResponse)
async def rec_pin_ciudadano(request: Request):
    return await handle_post_recuperar_pin_ciudadano(request)

