from passlib.hash import pbkdf2_sha256
from flask import session as Flask_Session
import random
import string


# Functions for Local Authentication
def Create_Hash(Password):
    return pbkdf2_sha256.hash(Password)


def Verify_Hash(Password, Hash):
    return pbkdf2_sha256.verify(Password, Hash)
