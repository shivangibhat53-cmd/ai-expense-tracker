from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.logging import logger
logger.info("***********Inside auth service.py *********")
def create_user(db : Session, email :str, password : str):
    user = User(
        email = email,
        hashes_password = hash_password(password)
    )
    db.add(user)
    logger.INFO("USER ADDED")
    db.commit()
    logger.INFO("USER COMMITTED")
    db.refresh(user)
    logger.INFO("USER REFRESHED")

    return user

def authenticate_user(db:Session, email:str, password :str):
    user = db.query(User).filter(User.email == email).first()
    logger.INFO("AUTHENTICATING USER")
    if not user:
        # Generate a dummy verification step that mimics standard bcrypt computation time.
        # This keeps server response times identical whether an email exists or not. Timimg Attack Mitigation
        dummy_hash = "$2b$12$L7R6DksbH29Vj/5RsmP9be2M7g1wXq/O8p4B76L.bWwZEmwN0gTGW"
        verify_password(password, dummy_hash)
        return None
    
    if not verify_password(password, user.hashes_password):
        return None
    
    return user