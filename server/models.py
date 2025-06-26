from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationships
    recipes = db.relationship(
        'Recipe',
        backref='user',
        cascade='all, delete-orphan'
    )

    # Serialization rules
    serialize_rules = ('-password_hash', '-_password_hash', 'recipes')

    @validates('username')
    def validate_username(self, _, username):
        if not username or not username.strip():
            raise ValueError("Username must not be empty.")
        return username

    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Serialization rules
    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self, _, title):
        if not title or not title.strip():
            raise ValueError("Title must not be empty.")
        return title

    @validates('instructions')
    def validate_instructions(self, _, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters.")
        return instructions

    @validates('minutes_to_complete')
    def validate_minutes_to_complete(self, _, minutes):
        if not isinstance(minutes, int) or minutes <= 0:
            raise ValueError("Minutes must be a positive integer.")
        return minutes
