from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Gebruiker(Base):

    __tablename__ = "Gebruiker"

    GebruikerId = Column(Integer, primary_key=True)
    OrganisatieID = Column(Integer)
    Gebruikersnaam = Column(String)
    SaltedHash = Column(String)
    Actief = Column(Boolean)
    RedenBlokkade = Column(String)
    Voornaam = Column(String)
    Tussenvoegsel = Column(String)
    Achternaam = Column(String)
    Geslacht = Column(String)
    Emailadres = Column(String)
    UID = Column(String)
