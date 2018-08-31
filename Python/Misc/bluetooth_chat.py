import bluetooth
from pykeyboard import PyKeyboard

k = PyKeyboard()

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1
server_socket.bind(("", port))
server_socket.listen(1)
client_socket, address = server_socket.accept()

print('Accepted connection from', address)

while True:
    try:
        data = client_socket.recv(1024)
        s = data.decode()
        if len(s)>0:    
#            print('Received: ' + s)
            k.type_string(s)
            print()
        client_socket.send("Hello From Pi !!!")
        client_socket.send('\n')
    except:
        print('Connexion closed')
        break
client_socket.close()
server_socket.close()
