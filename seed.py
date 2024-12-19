"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Book, Read


db.drop_all()
db.create_all()

with open('generator/bookclubusers.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/books.csv') as books:
    db.session.bulk_insert_mappings(Book, DictReader(books))

with open('generator/reads.csv') as reads:
    db.session.bulk_insert_mappings(Read, DictReader(reads))

db.session.commit()
