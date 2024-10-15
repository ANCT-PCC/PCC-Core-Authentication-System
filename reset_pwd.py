import hashlib
new_pwd = input("Enter new password: ")
hashed_pwd = hashlib.sha256(new_pwd.encode("utf-8")).hexdigest()

print(hashed_pwd)