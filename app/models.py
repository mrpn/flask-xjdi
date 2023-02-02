from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.orm import declarative_base


Base = declarative_base()

roles_ref = db.Table("roles_ref",
    db.Column("user_id", db.BigInteger, db.ForeignKey("user.id")),
    db.Column("role_id", db.BigInteger, db.ForeignKey("role.id")),
)

characters_ref = db.Table("characters_ref",
    db.Column("user_id", db.BigInteger, db.ForeignKey("user.id")),
    db.Column("character_id", db.Integer, db.ForeignKey("character.id")),
)

bidders_ref = db.Table("bidders_ref",
    db.Column("user_id", db.BigInteger, db.ForeignKey("user.id")),
    db.Column("bid_id", db.Integer, db.ForeignKey("loot.id")),
)

winners_ref = db.Table("winners_ref",
    db.Column("user_id", db.BigInteger, db.ForeignKey("user.id")),
    db.Column("win_id", db.Integer, db.ForeignKey("loot.id")),
)

scouts_ref = db.Table("scouts_ref",
    db.Column("user_id", db.BigInteger, db.ForeignKey("user.id")),
    db.Column("win_id", db.Integer, db.ForeignKey("loot.id")),
)

class User(UserMixin, db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    discord_locale = db.Column(db.String(7), unique=False, index=False, nullable=True)
    name = db.Column(db.String(240), unique=False, index=False, nullable=True)
    avatar = db.Column(db.String(240), unique=False, index=False, nullable=True)
    joined = db.Column(db.DateTime, unique=False, index=False, nullable=True)
    last_login = db.Column(db.DateTime, unique=False, index=False, nullable=True)
    created = db.Column(db.DateTime, unique=False, index=False)
    key_role = db.Column(db.BigInteger, db.ForeignKey("role.id"), index=True, nullable=True)
    key_role_name = db.relationship("Role", foreign_keys=key_role)
    is_approved = db.Column(db.Boolean, unique=False, index=False, nullable=True, default=False)
    is_staff = db.Column(db.Boolean, unique=False, index=False, nullable=True, default=False)
    is_admin = db.Column(db.Boolean, unique=False, index=False, nullable=True, default=False)
    is_member = db.Column(db.Boolean, unique=False, index=False, nullable=True, default=False)
    discord_roles = db.relationship('Role', secondary=roles_ref, back_populates='discord_users', lazy='joined')
    characters = db.relationship('Character', secondary=characters_ref, back_populates='characters', lazy='dynamic')
    screenshot = db.Column(db.String(240), unique=False, index=False, nullable=True)
    bids = db.relationship('Loot', secondary=bidders_ref, back_populates='bidders', lazy='dynamic')
    wins = db.relationship('Loot', secondary=winners_ref, back_populates='winners', lazy='dynamic')
    def __repr__(self):
        return '<User {}>'.format(self.id) 

class Role(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(240), unique=False, nullable=False, index=False)
    position = db.Column(db.Integer, unique=False, nullable=False, index=False)
    color = db.Column(db.Integer, unique=False, nullable=False, index=False)
    updated = db.Column(db.DateTime, unique=False, index=False, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    discord_users = db.relationship('User', secondary=roles_ref, back_populates="discord_roles", lazy='joined')
    def __repr__(self):
        return '<Role {}>'.format(self.id)   

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, unique=False, nullable=False, index=False)
    created = db.Column(db.DateTime, unique=False, index=False, nullable=True, default=datetime.utcnow)
    author_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    comment_to_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    author = db.relationship("User", foreign_keys=[author_id])
    comment_to = db.relationship("User", foreign_keys=[comment_to_id])
    def __repr__(self):
        return '<Comment {}>'.format(self.id)  

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240), unique=False, index=False, nullable=True)
    created = db.Column(db.DateTime, unique=False, index=False, nullable=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, unique=False, index=False, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    is_ingame = db.Column(db.Boolean, unique=False, index=False, nullable=True, default=False)
    owner = db.relationship("User", foreign_keys=[owner_id])
    characters = db.relationship('User', secondary=characters_ref, back_populates="characters", lazy='dynamic')
    def __repr__(self):
        return '<Character {}>'.format(self.id)  