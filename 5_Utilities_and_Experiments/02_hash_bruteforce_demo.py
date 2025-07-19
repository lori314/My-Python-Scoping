import hashlib
import itertools

def generate_password_candidates(length=8, charset="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    return (''.join(p) for p in itertools.product(charset, repeat=length))

def check_password_candidates(stored_hash, candidates):
    for candidate in candidates:
        if authenticate(candidate, stored_hash):
            print(f"Found matching password: {candidate}")
            return
    print("No matching password found.")

def authenticate(input_password, stored_hash):
    input_hash = hashlib.sha256(input_password.encode())
    input_hash_value = input_hash.hexdigest()
    if input_hash_value == stored_hash:
        return True
    else:
        return False

stored_hash = "a265f9dc06656256bb3cf8ed64216e3ce918be2924ee7426f91425485ac0b9ed8"  # 假设这是存储的哈希值

candidates = list(generate_password_candidates())
check_password_candidates(stored_hash, candidates)