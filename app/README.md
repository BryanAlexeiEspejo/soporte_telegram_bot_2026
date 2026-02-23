python -m app.main || uvicorn app.main:app --reload --port 80 #Inicia el API que debe estar siempre viva para almacenar los msg en el rabbitMQ
python -m app.consumidores.whatsapp_consumer #Otro proceso para el consumidor
ngrok http http://localhost:80
pip list

//Nota si el .env se cachea es necesario eliminar la tarea de proceso desde el SO por su PID
