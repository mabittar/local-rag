import bcrypt

hash_in_db = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/Iy"

passwords = ["localuser", "localuser123", "admin", "password", "123456"]

for p in passwords:
    result = bcrypt.checkpw(p.encode("utf-8"), hash_in_db.encode("utf-8"))
    print(f"Password '{p}': {result}")
