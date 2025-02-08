import secrets
import os
import base64

def generate_key(num_bytes, url_safe=False):
    """Generates a cryptographically secure random key.

    Args:
        num_bytes: The number of random bytes to generate.  The key length
            will depend on the encoding (hex, urlsafe, base64).
        url_safe: Whether to generate a URL-safe key (using base64 encoding).

    Returns:
        A string representing the generated key.
    """
    if url_safe:
        return secrets.token_urlsafe(num_bytes)
    else:
        return secrets.token_hex(num_bytes)

def generate_key_os_urandom(num_bytes):
    """
    Generate a url-safe secret key using os.urandom and base64 encoding.
    """
    key_bytes = os.urandom(num_bytes)
    return base64.urlsafe_b64encode(key_bytes).decode('utf-8')


if __name__ == '__main__':
    print("Generating Keys...\n")

    # Flask's SECRET_KEY (hexadecimal)
    secret_key = generate_key(32)  # 32 bytes = 256 bits
    print(f"Flask SECRET_KEY (hex): {secret_key}")
    print(f"  Length: {len(secret_key)} characters\n")

    # JWT Secret Key (URL-safe)
    jwt_secret_key = generate_key(64, url_safe=True)  # 64 bytes = 512 bits
    print(f"JWT SECRET_KEY (url-safe): {jwt_secret_key}")
    print(f"  Length: {len(jwt_secret_key)} characters\n")

    # JWT secret key (os.urandom and base64)
    jwt_secret_key_b64 = generate_key_os_urandom(64)
    print(f"JWT SECRET_KEY (os.urandom, base64): {jwt_secret_key_b64}")
    print(f"Length: {len(jwt_secret_key_b64)} characters")