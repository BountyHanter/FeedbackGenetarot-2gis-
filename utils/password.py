import os
from dotenv import load_dotenv

from cryptography.fernet import Fernet

load_dotenv()
KEY = os.getenv("ENCRYPTION_KEY").encode()


def decrypt_password(encrypted_password: str) -> str:
    """
    Расшифровывает пароль, используя указанный ключ.

    :param encrypted_password: Зашифрованный пароль (строка).
    :return: Расшифрованный пароль.
    """
    try:
        cipher = Fernet(KEY)
        decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
        return decrypted_password
    except Exception as e:
        raise ValueError(f"Failed to decrypt password: {e}")


def encrypt_password(password: str) -> str:
    """
    Шифрует пароль с использованием указанного ключа.

    :param password: Пароль в виде строки.
    :return: Зашифрованный пароль в виде строки.
    """
    try:
        # Преобразуем ключ в формат bytes
        cipher = Fernet(KEY)

        # Шифруем пароль
        encrypted_password = cipher.encrypt(password.encode())

        # Возвращаем зашифрованный пароль в формате строки
        return encrypted_password.decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt password: {e}")


if __name__ == "__main__":
    print(decrypt_password("gAAAAABnUteBVBwvtdNZ9UZT5o2ib61f3pVvwERH8FkYXt3CWK3wlWdZDD76ROuJxKOteS_qcpy5BUV4B3cxpBPztB3n7myzJg"))