from sqlalchemy.orm import Session

from backend.app.db import Users

USER_ORDER_MAP = {
        "id" : Users.id,
        "full_name" : Users.full_name,
        "email" : Users.email,
        "user_type" : Users.user_type,
        "password" : Users.password,
        "user_office" : Users.user_office,
        "is_disabled" : Users.is_disabled
    }

class UsersRepository():
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        """
        self.db = db

    def get_user_by_id(self, user_id):
        """
        Retrieve a user from the database by their ID.
        """
        return self.db.get(Users, user_id)
    
    def get_user_by_email(
            self,
            email: str
        ) -> Users | None:
        """
        Retrieve a user from the database by their email.
        """
        return self.db.query(Users).filter(Users.email == email).first()
    
    def get_password(self, user_id: int) -> Users | None:
        """
        Retrieve the hashed password of a user by their ID.
        """
        return self.db.get(Users, user_id)
        
    def create_user(self, user_data: dict):
        """
        Create and persist a new user database record.
        """
        new_user = Users(**user_data)
        self.db.add(new_user)

        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def update_user(
            self, 
            user_id: int,
            user_data: dict) -> Users | None:
        """
        Update the profile details of an existing user.
        """
        user = self.db.get(Users, user_id)

        if not user:
            return None
        
        for k, v in user_data.items():
            setattr(user, k, v)

        self.db.commit()
        self.db.refresh(user)

        return user
    
    def change_password(
            self,
            user_id: int,
            password: str) -> Users | None:
        """
        Update the password hash for a specific user.
        """
        user = self.db.get(Users, user_id)
        
        if not user:
            return None
        
        user.password = password

        self.db.commit()
        self.db.refresh(user)

        return user
    
    def change_user_status(
            self,
            user_id: int,
            user_status: bool):
        """
        Enable or disable a specific user.
        """
        user = self.db.get(Users, user_id)

        if not user:
            return None
        
        user.is_disabled = user_status

        self.db.commit()
        self.db.refresh(user)

        return user
    
    def get_users_by_filter(self, filters: dict) -> list[Users]:
        """
        Retrieve users matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Users)

        exact_filters = {
            "id": Users.id,
            "email": Users.email,
            "user_type": Users.user_type,
            "user_office": Users.user_office,
        }
        for key, column in exact_filters.items():
            if (value := filters.get(key)) is not None:
                query = query.filter(column == value)

        if (name := filters.get("full_name")) is not None:
            query = query.filter(Users.full_name.ilike(f"%{name}%"))

        if (status := filters.get("user_status")) is not None:
            query = query.filter(Users.is_disabled == status)

        order_col = USER_ORDER_MAP.get(filters.get("order_by"), Users.id)
        direction = filters.get("order_direction", "desc")

        if direction.lower() == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()