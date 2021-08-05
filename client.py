import socket, win32api, sys, win32con
from threading import Thread
from eventhook import EventHook



class TCPClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.on_connection = EventHook()
        self.on_message = EventHook()
        self.on_disconnection = EventHook()


    def __receive_messages(self):
        try:
            while True:
                message = self.socket.recv(1024)
                if message:
                    self.on_message.fire(socket=socket, message=message)
        except:
            self.on_disconnection.fire()

    def connect(self, ip: str, port: int) -> None:
        try:
            self.socket.connect((ip, port))
            self.on_connection.fire(socket=socket)
            Thread(target=self.__receive_messages, args=()).start()
        except:
            print("Failed to estabilish connection")
    
    def send_message(self, message) -> None:
        self.socket.send(message)


tcp_client = TCPClient()

def move_mouse(x, y) -> None:
    win32api.SetCursorPos((x, y))

def click_mouse(x, y):
    try:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
    except:
        pass


def on_connection(socket: socket.socket):
    print("Connection estabilished")

def on_message(socket: socket.socket, message):
    message_str = message.decode('ascii')
    
    if len(message_str.split("move")) > 2:
        return
    if len(message_str.split("click")) > 2:
        return

    message_split = message_str.split("*")
    action = message_split[0]
    message_split[1] = message_split[1].replace("move", "")
    message_split[2] = message_split[2].replace("move", "")
    message_split[1] = message_split[1].replace("click", "")
    message_split[2] = message_split[2].replace("click", "")
    
    x = int(float(message_split[1]))
    y = int(float(message_split[2]))
    if action == "move":
        move_mouse(x, y)
    elif action == "click":
        click_mouse(x, y)




def on_disconnection():
    print("Got disconnected.")



def main():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    
    tcp_client.on_connection.addHandler(on_connection)
    tcp_client.on_message.addHandler(on_message)
    tcp_client.on_disconnection.addHandler(on_disconnection)
    tcp_client.connect(ip, port)




if __name__ == "__main__":
    main()