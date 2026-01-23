from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Exception de base de l'application"""
    
    def __init__(
        self, 
        message: str, status_code: int = 400, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        # self.error_code = error_code or "ACL_ERROR"
        self.details = details
        super().__init__(self.message)


class NotFoundFailure(BaseAppException):
    """Resource non trouvée"""
    
    def __init__(self, field: str, error: str):
        super().__init__(
            message= "Resource non trouvée", 
            status_code=404,
            details=[{'field': field, 'message': error}]
        )
        
        

class UnAuthorisedFailure(BaseAppException):
    """Non autorisé"""
    
    def __init__(self, message: str = "Non authentifié"):
        super().__init__(
            message, status_code=401,
            details=[{'field': 'unauthorized', 'message': "Token invalide ou expiré."}]
        )
        


class ForbidenFailure(BaseAppException):
    """Accès interdit"""
    
    def __init__(self, message: str = "Accès interdit"):
        super().__init__(
            message, status_code=403, 
            details=[
                {
                    'field': 'forbiden', 
                    'message': "Vous n'avez pas la permission de faire cette action."
                }
            ]
        )    



class ConflictFailure(BaseAppException):
    """Conflit (ressource déjà existante, etc.)."""

    def __init__(self, field: str, error: str):
        super().__init__(
            message = "ressource déjà existante", 
            status_code=409, 
            details=[{'field': field, 'message': error}]
        )


class BadRequestFailure(BaseAppException):
    """Requète invalide."""

    def __init__(self, field: str, error: str):
        super().__init__(
            message= "Mauvaise Requète", 
            status_code=400, 
            details=[{'field': field, 'message': error}]
        )



class DatabaseFailure(BaseAppException):
    """Erreur de connexion à la base de données."""

    def __init__(self, message: str = "Erreur de connexion à la base de données"):
        super().__init__(message, status_code=500)