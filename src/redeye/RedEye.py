from Crypto import PublicKey
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes, new
import subprocess
import datetime
import sqlite3
import getpass
import random
import string
import time
import sys
import os

class Color:
    red = '\033[91m'
    green = '\033[92m'
    reset = '\033[90m'
"""
-----------------------------------------------
            Funciones Auxiliares
-----------------------------------------------
"""

def barra_simple(ancho=35, prefijo=""):

    total = 100

    for i in range(total + 1):
        porcentaje = i / total
        llenos = int(ancho * porcentaje)
        barra = "■" * llenos + "□" * (ancho - llenos)
        sys.stdout.write(f"\r{prefijo}[{barra}] {porcentaje:6.2%}")
        sys.stdout.flush()
        time.sleep(0.02)
        if i == total:
            print()
    
def narrar(texto, delay_min=0.03, delay_max=0.25):
    for c in texto:
        sys.stdout.write(c)
        sys.stdout.flush()
        if c in ".!?":
            time.sleep(random.uniform(0.25, 0.5))
        elif c in ",;:":
            time.sleep(random.uniform(0.1, 0.25))
        elif c in "=<>$":
            time.sleep(0.001)
        else:
            time.sleep(random.uniform(delay_min, delay_max))
    print()


class DataBase:
    def __init__(self) -> None:
        self.DB = 'RedEye.db'
        self.conn, self.cur = self.conectar()
        self.crear_tabla()
        pass

    def conectar(self):
        conn = sqlite3.connect(self.DB)
        cur = conn.cursor()
        return conn, cur

    def crear_tabla(self) -> bool:
        tabla = self.cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        admin BOOL NOT NULL,
        public_key TEXT UNIQUE,
        private_key TEXT UNIQUE
        )''')
        if tabla:
            self.conn.commit()
            return True
        else: return False

    def create_user(self, user: str, password:str) -> bool:
        insert_user = self.cur.execute('''INSERT INTO users (user, password, admin) VALUES(?, ?, ?)''', (user, password, 'False'))
        if insert_user:
            self.conn.commit()
            return True
        else: return False

    def verify_password(self, user: str) -> str:
        self.cur.execute('''SELECT password FROM users WHERE user = ?''', (user,))
        password = self.cur.fetchone()
        return password

    def change_password(self, user: str, new_password: str) -> bool:
        change = self.cur.execute('''UPDATE users SET password = ? WHERE user = ?''', (user, new_password))
        if change:
            self.conn.commit()
            return True
        else: return False

    def verify_user(self, user: str, password: str) -> str: #OR None
        '''Devuelve todo lo relacionado con el usuario si existe'''
        self.cur.execute("SELECT * FROM users WHERE user = ? AND password = ?", (user, password))       
        info = self.cur.fetchone()
        return info #(id, 'user', 'password', admin=Bool, private_key, private_key)
    
    def insert_key(self, new_key: str, user_modified: str, is_private: bool) -> bool:

        if is_private:
            if self.cur.execute("UPDATE users SET private_key = ? WHERE user = ?", (new_key, user_modified)):
                return True
            else: return False
        else:
            if self.cur.execute("UPDATE users SET public_key = ? WHERE user = ?", (new_key, user_modified)):
                return True
            else: return False

    def disponibilidad(self) -> str:
        self.cur.execute("SELECT * FROM users")
        usuarios = self.cur.fetchall()
        cantidad = 0
        for _ in usuarios:
            cantidad += 1
        if cantidad <= 1:
            return "Disponible"
        else: return "No disponible"

def login():

    usuario = {
            "user": None, 
            "password": None,
            "admin": False,
            "public_key": None,
            "private_key": None
            }

    narrar(f"{"=" * 18}Autenticacion:{"=" * 18}\n\n")

    while True:
        try:
            user = input("Usuario: ")
            password = getpass.getpass("Contraseña: ", echo_char='*')
            if user == ('') or password == ('') and password not in (string.punctuation + string.ascii_lowercase + string.ascii_uppercase):
                raise ValueError
            DB = DataBase()
            info = DB.verify_user(user=user, password=password)
            if info is not None:
                usuario["user"] = info[1]
                usuario["password"] = info[2]
                usuario["admin"] = info[3]
                usuario["private_key"] = info[4]
                usuario["public_key"] = info[5]
                return usuario
            else:
                disponible = DB.disponibilidad()
                narrar(f"\n{Color.red}Usuario o contraseña incorrecto{Color.reset}")
                narrar(f"Opciones: \n\t1. Volver a intentar\n\t2. Crear nuevo usuario ({disponible})\n\t3. Salir")
                opt = int(input("> "))
                if opt == 1:
                    continue
                elif opt == 2:
                    if disponible == "Disponible":
                        user = input("Usuario: ").strip()
                        password = getpass.getpass("\nContraseña: ").strip()
                        if user == " " or password == " " or user not in (string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation) or password not in (string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation):    
                            nuevo_usuario = DB.create_user(user=user, password=password)
                            if nuevo_usuario:
                                usuario["user"] = user
                                usuario["password"] = password
                                narrar(f"Usuario creado")
                                time.sleep(0.05)
                                return usuario
                            else:
                                narrar(f"\n{Color.red}[CRÍTICO]No se pudo crear el usuario. Saliendo del programa ahora{Color.reset}")
                                sys.exit(0)
                        else: raise ValueError
                    else: 
                        narrar(f"\n{Color.red}Ya existe un usuario{Color.reset}")
                elif opt == 3:
                    narrar(f"Saliendo del programa ahora\n Adios")
                    sys.exit(0)

                else:
                    narrar(f"\n{Color.red}Opción: {opt} no válida{Color.reset}")
                    continue

        except ValueError:
            narrar(f"{Color.red}Usuario o contraseña incorrecta. Por favor use caracteres comunes{Color.reset}")
            continue

        except Exception as e:
            print("Error: ", e)

def main():
    DB = DataBase()
    narrar("Iniciando proyecto RedEye")
    barra_simple(prefijo="Cargando")
    narrar("Se necesita autenticación\nProcediendo...")

    while True:
        usuario = login()
        subprocess.run("clear")
        print("=" * 54)
        narrar("\t\t\tRedEye")
        print("=" * 54)
        narrar(f"\nBienvenido {usuario['user']}")
        break
main()
#FIXME: Hashear la contraseña del usuario y el PrivateKey antes de guardarlo en la base de datos
#FIXME: Revisar el 'validador' de contraseñas esta dejando meter cualquier caracter
#FIXME: Revisar la funcion de disponibilidad antes de crear un usuario. esta dejando crear un usuario aunque ya exista uno
