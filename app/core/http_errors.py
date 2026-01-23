from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions.exceptions import BaseAppException



def custom_exception(app: FastAPI):
    
    @app.exception_handler(BaseAppException)
    async def custom_exception_handler(request: Request, exc: BaseAppException):
        """Gère les exceptions personnalisées de l'application."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "errors": exc.details
            }
        )


def validation_exception(app: FastAPI):
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors_list = []
        for error in exc.errors():
            field_path = error["loc"]
            # Gestion spéciale pour les éléments de liste
            if len(field_path) >= 2 and field_path[0] == "body":
                # Enlève "body" du chemin
                field_path = field_path[1:]
                
                if len(field_path) >= 2 and isinstance(field_path[-2], int):
                    field_name = f"{field_path[-1]}_{field_path[-2]}"
                else:
                    field_name = "_".join(str(part) for part in field_path)
            else:
                field_name = "_".join(str(part) for part in field_path)
            
            errors_list.append({
                "field": field_name,
                "message": error["msg"][13:]  # ou juste error["msg"]
            })
        return JSONResponse(
            status_code=400, 
            content={
                'success': False,
                'message': "Erreur validation",
                'errors': errors_list
            },
        )



def generic_exception(app: FastAPI):
    # Exception handler pour les erreurs génériques
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Gère les exceptions non gérées."""

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "errors": str(exc)
            }
        )