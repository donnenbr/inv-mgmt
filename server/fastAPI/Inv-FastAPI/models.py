# coding: utf-8
from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

from form_models import *

metadata_obj = MetaData()
Base = declarative_base(metadata = metadata_obj)

class ContainerType(Base):
    __tablename__ = 'container_type'
    __table_args__ = (
        CheckConstraint('can_hold_sample in (0,1)'),
        CheckConstraint('can_move in (0,1)'),
        CheckConstraint('number_columns is null or number_columns >= 0'),
        CheckConstraint('number_rows is null or number_rows >= 0')
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    number_rows = Column(Integer)
    number_columns = Column(Integer)
    can_hold_sample = Column(Boolean, nullable=False, server_default=text("0"))
    can_move = Column(Boolean, nullable=False, server_default=text("0"))


class Reagent(Base):
    __tablename__ = 'reagent'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    smiles = Column(String(256))


class Lot(Base):
    __tablename__ = 'lot'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    reagent_id = Column(ForeignKey('reagent.id'), nullable=False)

    reagent = relationship('Reagent')


class Container(Base):
    __tablename__ = 'container'

    id = Column(Integer, primary_key=True)
    barcode = Column(String(20), nullable=False, unique=True)
    type_id = Column(ForeignKey('container_type.id'), nullable=False)
    lot_id = Column(ForeignKey('lot.id'), index=True)
    amount = Column(Float)
    unit = Column(String(8))
    concentration = Column(Float)
    concentration_unit = Column(String(8))

    lot = relationship('Lot')
    type = relationship('ContainerType')


class ContainerContainer(Base):
    __tablename__ = 'container_container'

    id = Column(Integer, primary_key=True)
    container_id = Column(ForeignKey('container.id'), unique=True)
    parent_container_id = Column(ForeignKey('container.id'), nullable=False, index=True)
    position = Column(String(8), nullable=False)

    container = relationship('Container', primaryjoin='ContainerContainer.container_id == Container.id')
    parent_container = relationship('Container', primaryjoin='ContainerContainer.parent_container_id == Container.id')
