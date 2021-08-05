import socket, sys, ctypes
from threading import Thread
from eventhook import EventHook
from pynput.mouse import Listener

class TCPServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_connection = EventHook()
        self.on_message = EventHook()
        self.on_disconnection = EventHook()
        self.clients = []

    def __receive_message(self, conn: socket.socket):
        try:
            while True:
                message = conn.recv(1024)
                if message:
                    self.on_message.fire(socket=conn, message=message)

        except Exception as e:
            print(e)
            self.on_disconnection.fire()
            self.clients.remove(conn)

    def __receive_connections(self):
        try:
            conn, addr = self.socket.accept()
            self.clients.append(conn)
            self.on_connection.fire(socket=conn, address=addr)
            Thread(target=self.__receive_message, args=[conn]).start()
            Thread(target=self.__receive_connections, args=()).start()

        except:
            print("Failed to receive connection")
    
    def start(self, ip: str, port: int) -> None:
        try:
            self.socket.bind((ip, port))
            self.socket.listen()
            thread = Thread(target=self.__receive_connections, args=())
            thread.start()
        except:
            print("Failed to start server")

    def send_message(self, message) -> None:
        for client in self.clients:
            client.send(message)


tcp_server = TCPServer()

def on_connection(socket: socket.socket, address: ctypes.Array) -> None:
    print("[+] A client has been connected\nAddress: {0}".format(address[0]))

def on_message(socket: socket.socket, message) -> None:
    pass


def on_disconnection() -> None:
    print("[-] A client has disconnected")


def on_move(x, y) -> None:
    message_str = "move*{0}*{1}".format(x, y)
    message_bytes = message_str.encode('ascii')
    tcp_server.send_message(message_bytes)

def on_click(x, y, button, pressed) -> None:
    if not pressed:
        return

    message_str = "click*{0}*{1}".format(x, y)
    message_bytes = message_str.encode('ascii')
    tcp_server.send_message(message_bytes)

def on_scroll(x, y, dx, dy) -> None:
    pass

def main():
    ip = sys.argv[1]
    port = int(sys.argv[1])
    tcp_server.on_connection.addHandler(on_connection)
    tcp_server.on_message.addHandler(on_message)
    tcp_server.on_disconnection.addHandler(on_disconnection)
    tcp_server.start(ip, port)
    print("[+] Server started.")
    with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        print("[+] Mouse hooks successfully enabled")
        listener.join()


        

if __name__ == "__main__":
    main()