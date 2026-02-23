def _opciones_catastro(self) -> dict:
    campos = [
        {
            "title": "Servicios catastrales",
            "rows": [
                {
                    "id": "catastro-a",
                    "title": "Opción (A)",
                    "description": "Consulta tu trámite",
                },
                {
                    "id": "catastro-b",
                    "title": "Opción (B)",
                    "description": "Requisitos para trámites en catastro.",
                },
                {
                    "id": "catastro-c",
                    "title": "Opción (C)",
                    "description": "Puntos y horarios de atención",
                },
                {
                    "id": "catastro-d",
                    "title": "Opción (D)",
                    "description": "Preguntas frecuentes",
                },
                {
                    "id": "catastro-e",
                    "title": "Opción (E)",
                    "description": "Contactos y direcciones",
                },
            ],
        }
    ]
    return campos
