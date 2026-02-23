# setup_telegram.py
import os
import requests
import sys
from dotenv import load_dotenv, set_key

load_dotenv()

def setup_telegram_bot():
    """Guía para configurar el bot de Telegram"""
    print("=" * 60)
    print("CONFIGURACIÓN DEL BOT DE TELEGRAM")
    print("=" * 60)
    
    # 1. Token
    token = input("\n📝 Pega tu TOKEN de BotFather: ").strip()
    if not token:
        print("❌ Se necesita un token")
        return
    
    # Verificar token
    print("\n✅ Verificando token...")
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                print(f"   ✅ Token válido!")
                print(f"   🤖 Bot: @{bot_info['result']['username']}")
                print(f"   📝 Nombre: {bot_info['result']['first_name']}")
                
                # Guardar en .env
                set_key(".env", "TELEGRAM_BOT_TOKEN", token)
                print("   ✅ Token guardado en .env")
            else:
                print("❌ Token inválido")
                return
        else:
            print("❌ Error verificando token")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Obtener ID de admin
    print("\n📱 Para obtener tu ID de administrador:")
    print("   1. Abre Telegram")
    print("   2. Busca: @userinfobot")
    print("   3. Envía /start")
    print("   4. Copia tu ID (solo números)")
    
    admin_id = input("\n📝 Ingresa tu ID de admin: ").strip()
    if admin_id and admin_id.isdigit():
        set_key(".env", "TELEGRAM_ADMIN_ID", admin_id)
        print("✅ ID de admin guardado")
    else:
        print("⚠️  ID no válido, puedes configurarlo después")
    
    # 3. Configurar webhook
    print("\n🌐 Configuración del Webhook:")
    print("   1. Para desarrollo: Usa ngrok (recomendado)")
    print("   2. Ejecuta en otra terminal: ngrok http 8000")
    print("   3. Copia la URL HTTPS que te da ngrok")
    
    webhook_url = input("\n📝 Pega la URL de ngrok (ej: https://abc123.ngrok-free.app): ").strip()
    
    if webhook_url:
        full_url = f"{webhook_url}/telegram/webhook"
        
        # Configurar webhook en Telegram
        set_webhook_url = f"https://api.telegram.org/bot{token}/setWebhook"
        payload = {
            "url": full_url,
            "drop_pending_updates": True
        }
        
        try:
            resp = requests.post(set_webhook_url, json=payload)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("ok"):
                    set_key(".env", "TELEGRAM_WEBHOOK_URL", full_url)
                    print(f"✅ Webhook configurado: {full_url}")
                else:
                    print(f"❌ Error: {result.get('description')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("=" * 60)
    print("\n🚀 Pasos siguientes:")
    print("   1. python -m uvicorn app.main:app --reload")
    print("   2. ngrok http 8000 (en otra terminal)")
    print("   3. Ve a Telegram y busca: @Agente_municipal_ami_bot")
    print("   4. Escribe /start")

if __name__ == "__main__":
    setup_telegram_bot()