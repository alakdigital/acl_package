from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from alak_acl.shared.exceptions import ACLException

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ACLException)
    async def acl_exception_handler(request: Request, exc: ACLException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "errors": exc.details,
                "path": request.url.path,
            },
        )
        
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Gère les exceptions non gérées."""
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "errors": str(exc),
                "path": request.url.path,
            }
        )
        
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
                'errors': errors_list,
                "path": request.url.path,
            },
        )

        
     