import jwt

JWT_SECRET_KEY = "mukeshnautiyal"
def generate_jwt_token(content):
    encoded_content = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")
    token = str(encoded_content).split("'")[1]
    return token
    
    
def validate_user(email, password):
    #print(email,len(email))
    #current_user = db_read("""SELECT * FROM users WHERE email = %s""", (email,))
    #print(len(email))
    if len(email) >= 1:
        #saved_password_hash = email.password
        #saved_password_salt = email.password
        #print(saved_password_hash,saved_password_salt,"saved_password_salt")
        #password_hash = generate_hash(password, saved_password_salt)

        #if password_hash == saved_password_hash:
        user_id = email['id']
        jwt_token = generate_jwt_token({"id": user_id})
        #print(jwt_token,"jwt_token")
        return jwt_token
        """else:
            return False"""

    else:
        return False