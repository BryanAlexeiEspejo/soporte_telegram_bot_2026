import os   
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
#import tiktoken
cliente_contexto = OpenAI(
   
   
    api_key=os.getenv("AI_KEY"),
    base_url=os.getenv("AI_URL"),
)
system_rol = '''Eres un recepcionista que devuelve en un numero todo el contexto que un interlocutor te da,
                si te habla de contraseñas, pin o igob, devuelves 1,
                si te habla de trámites o licencias devuelves 2,
                si te habla de cualquier contexto catastral o propiedad inmueble devuelves 3,
                si te habla de cualquier asunto sanitario o salud para personas devuelves 4,
                si te habla de atencion municipal a ciudadanos devuelves 5,
                si te habla de mascotas o cualquier cosa relacionada devuelves 6
                si te habla de limpieza, deshierbado o el programa comunitario llamado -100 jueves- devuelves 7,
                si no te habla de nada de eso devuelves 8.'''

contextos = {   1: "igob",
                2: "tramites",
                3: "catastro",
                4: "hospitales",
                5: "ciudadano",
                6: "veterinaria",
                7: "limpieza",
                8: ""  } 
 
async def consultar_contexto_ia(user_prompt: str) -> str:
    try:
        respuesta = cliente_contexto.chat.completions.create(
        model="gpt-4",
        max_tokens=8,
        messages=[
                    {"role": "system", "content": system_rol},
                    {"role": "user", "content": user_prompt}
                ]
            )
        respuesta_assistan = respuesta.choices[0].message.content
        numero = int(respuesta_assistan)
        contexto = contextos.get(numero)
        if contexto:
            return contexto
        else:
            # print("No se encontró contexto para el número:", numero)
            return None
    except ValueError:
        #print("La IA no devolvió un número válido:", respuesta_assistan)
        return None
    except Exception as e:
        #print(f"Error al conectar con OpenAI: {e}")
        return None

# while True:
#     user_prompt = input("\x1b[1;33m" + "\nDime algo porfa:")
#     resultado = consultar_contexto_ia(user_prompt)
#     print("-contexto->", resultado)