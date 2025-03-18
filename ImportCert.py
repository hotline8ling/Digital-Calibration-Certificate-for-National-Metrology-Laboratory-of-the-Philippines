import os

filepath = input('Enter the path of the certificate: ')
os.cd(os.system('certutil -addstore -f "Root" ' + filepath))