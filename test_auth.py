from app.auth.pwd_utils import get_password_hash, verify_password

def test_auth():
    password = "secure_password_123"
    print(f"Original Password: {password}")
    
    # Test hashing
    hashed = get_password_hash(password)
    print(f"Hashed Password: {hashed}")
    
    # Test verification
    is_valid = verify_password(password, hashed)
    print(f"Verification Success: {is_valid}")
    
    # Test wrong password
    is_invalid = verify_password("wrong_password", hashed)
    print(f"Wrong Password Rejected: {not is_invalid}")
    
    # Test UTF-8 support
    utf8_password = "password_with_é_ü_ñ"
    utf8_hashed = get_password_hash(utf8_password)
    utf8_valid = verify_password(utf8_password, utf8_hashed)
    print(f"UTF-8 Password Support: {utf8_valid}")
    
    if is_valid and not is_invalid and utf8_valid:
        print("\nALL AUTH TESTS PASSED!")
    else:
        print("\nAUTH TESTS FAILED!")

if __name__ == "__main__":
    test_auth()
