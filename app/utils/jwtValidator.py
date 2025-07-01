import sys
import jwt
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.secretManager import SecretManager
from app.utils.logger import Logger

#Clase para validar JWT
class JWTValidator:
    def __init__(self):
        self.secret_key = SecretManager().get_secretJWT()
        self.log = Logger("app/logs/jwtValidator.log").get_logger()

    def validate_token(self, token):
        try:
            # Decoding the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            self.log.error("Token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            self.log.error("Invalid token")
            raise ValueError("Invalid token")
        except Exception as ex:
            self.log.warning(f"An error occurred while validating the token: {str(ex)}")
            raise ValueError(f"An error occurred while validating the token: {str(ex)}")
    
    def get_user_info(self, token):
        try:
            payload = self.validate_token(token)
            email = payload.get("email")
            name = payload.get("name")
            return email, name
        except ValueError as ex:
            self.log.error(f"Error getting user info: {str(ex)}")
            raise ex
        except Exception as ex:
            self.log.error(f"An error occurred while getting user info: {str(ex)}")
            raise ValueError(f"An error occurred while getting user info: {str(ex)}")