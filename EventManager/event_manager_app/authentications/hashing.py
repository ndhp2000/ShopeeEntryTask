import base64
import bcrypt
import hashlib


class HashingUtil:
    def __init__(self, raw_str):
        self.raw_str = base64.b64encode(hashlib.sha256(raw_str.encode()).digest())

    def hash(self):
        """
        Hash raw_str with bcrypt algo
        :return: str
        """
        hashed_str = bcrypt.hashpw(self.raw_str, bcrypt.gensalt(4))
        return hashed_str.decode()

    def compare_hash(self, hashed_str):
        """
        Compare self.password with a hashed password
        :param hashed_str:
        :return: boolean
        """
        # CACHE
        return bcrypt.checkpw(self.raw_str, hashed_str.encode())
