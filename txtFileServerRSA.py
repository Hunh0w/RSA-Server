#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socketserver,socket,sys
from math import ceil

# Clé privé
n=0x00a6e992a702c03e238c0b80f3766c0de8c30e4f4dd021da7e53b7b07d716e3082e23a74494e879e5fb76858a220db7820f72de7db615a5c51192b26e704ce4c1cc9c3eae3019ff48ffbcbd5ee941be1f8601e6b77662596b8783d08182b63af8b9c55d0ebc869b6c3576c0c4ea09aef3418e57e31ef86e6c6c866026e5274bef7
e=65537

class ClientHandler(socketserver.BaseRequestHandler):
  def sendstrCipher(self, sfd, msgStr):
    
    nbPaquets=ceil(len(msgStr)/128)
    j=0
    self.sendstr(sfd, str(nbPaquets))
    for i in range(nbPaquets):
      paquet = msgStr[j:j+128]
      M=int.from_bytes(bytes(paquet,'utf-8'),byteorder='big')
      C=pow(M, e, n)
      strcipher = hex(C)
      self.sendstr(sfd, strcipher)
      j+=128

  def recvstr(self,sfd):
    msg=sfd.readline().rstrip()
    print("<=",msg)
    return msg
  def sendstr(self,sfd,out):
    print("=>",out)
    sfd.writelines(out+'\n')
    sfd.flush()
  def handle(self): 
    print("Start client",self.client_address)
    sfd=self.request.makefile('rw',encoding='utf-8')
    prompt = socket.gethostname()
    self.sendstr(sfd,prompt)
    while True:
      fileName=self.recvstr(sfd)
      if fileName == "@bye": break
      try:
        file = open(fileName, "r")
        lines = file.read()
        file.close()
        linescount = lines.count("\n")
        if linescount <= 0 or lines == None:
            self.sendstr(sfd, "0")
            continue
        if linescount > 10:
            self.sendstrCipher(sfd, "Erreur: Le fichier est trop gros")
            continue
        self.sendstrCipher(sfd, lines)
      except OSError as err:
        self.sendstrCipher(sfd, "Erreur de fichier '{}': [Errno {}] {}".format(fileName, err.errno, err.strerror))        

    print("Client %s déconnecté" % self.client_address[0])

socketserver.TCPServer.allow_reuse_address=True
s=socketserver.ThreadingTCPServer(('0.0.0.0',9876),ClientHandler)
print("Le serveur RSA vient de démarrer")
try:
  s.serve_forever()
except KeyboardInterrupt:
  s.shutdown()
  s.socket.close()
