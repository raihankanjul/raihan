import string

# Fungsi untuk membuat tabel substitusi
def create_cipher_table(key):
    alphabet = string.ascii_uppercase
    table = str.maketrans(alphabet, key)
    return table

# Fungsi untuk enkripsi
def encrypt(plaintext, table):
    return plaintext.upper().translate(table)

# Fungsi untuk dekripsi
def decrypt(ciphertext, table):
    reversed_table =str.maketrans(table, string.ascii_uppercase)
    return ciphertext.upper().translate(reversed_table)

# Fungsi utama
def main():
    # Membuat kunci untuk tabel substitusi
    key = 'BCDEFGHIJKLMNOPQRSTUVWXYZA'
    cipher_table = create_cipher_table(key)

    # Contoh penggunaan enkripsi
    plaintext = "KANJUL TIDUR"
    encrypted_text = encrypt(plaintext, cipher_table)
    print(f"Plainteks: {plaintext}")
    print(f"Cipherteks: {encrypted_text}")

    # Contoh penggunaan dekripsi
    decrypted_text = decrypt(encrypted_text, cipher_table)
    print(f"Kembali ke plainteks: {decrypted_text}")

if __name__ == "__main__":
    main()