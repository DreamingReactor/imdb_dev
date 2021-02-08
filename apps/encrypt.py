from passlib.hash import pbkdf2_sha256 as sha256

class Encrypt:
    def generate_hash(self, password):
        return sha256.hash(password)
    def verify_hash(self, password, hash):
        return sha256.verify(password, hash)