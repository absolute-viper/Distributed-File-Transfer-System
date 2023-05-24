import os
import socket
import time

master_server_ip = '10.113.6.121'
master_server_port = 9000
storage_directory = "./Client_Storage/"
SEPARATOR = "<sep>"

extensions = {
    "jpg": "images", "png": "images", "ico": "images", "gif": "images", "svg": "images",
    "mp3": "audio", "wav": "audio",
    "mp4": "video", "m3u8": "video", "webm": "video", "ts": "video",
    "pdf": "document", "xlsx": "document", "csv": "document", "docx": "document", "txt": "document",
    "pptx": "document", "ppt": "document"
}


def type_assigner(file_loc):   # Assigns type of the file being uploaded
    file_name = file_loc.split('/')[-1]
    ext = file_name.split('.')[-1]
    file_type = ""
    if ext in extensions:
        file_type = extensions[ext]
    if file_type == 'document':
        return 'document'
    elif file_type == 'images':
        return 'image'
    elif file_type == 'audio' or file_type == 'video':
        return 'audio/video'


def file_name_retriever(file_path):
    return file_path.split('/')[-1]


def client_send(client, file_path, file_type):
    file_name = file_name_retriever(file_path)
    path = os.path.join(storage_directory, file_name)
    file_size = os.path.getsize(path)
    client.send(f"{file_name}{SEPARATOR}{file_size}".encode())
    print("Sending to Master")
    if file_type == 'document':
        time.sleep(2)
        file = open(path, "r")
        data = file.read()
        client.send(data.encode())
        file.close()

    elif file_type == 'image':
        file = open(path, "rb")
        client.sendall(file)
        # image_data = file.read(2048)
        # while image_data:
        #     client.send(image_data)
        #     image_data = file.read(2048)
        # file.close()
        # print("All chunks sent")



def client_receive(client, file_name, file_type):
    path = os.path.join(storage_directory, file_name)
    if file_type == 'document':
        file = open(path, "w")
        data = client.recv(1024).decode()
        file.write(data)
        file.close()
        print("Completed")

    elif file_type == 'image':
        file = open(path, "wb")
        image_chunk = client.recv(2048)  # stream-based protocol
        while image_chunk:
            file.write(image_chunk)
            image_chunk = client.recv(2048)
        file.close()


def client_driver():
    """ Connecting to the Master Server """
    client = socket.socket()
    try:
        client.settimeout(5)
        client.connect((master_server_ip, master_server_port))
        client.settimeout(None)
        print("Connected to Master Storage Server {0}".format(master_server_ip))
    except Exception as e:
        print("Could not Connect to Master {0} {1}".format(master_server_ip, e))

    while True:
        print(client.recv(1024).decode())
        inp = input("Client: Enter an Option:")

        if inp == "1":
            client.send(inp.encode())
            print(client.recv(1024).decode())  # msg1
            file_path = input("Client: Enter file Path:")
            file_type = type_assigner(file_path)
            time.sleep(2)
            client_send(client, file_name_retriever(file_path), file_type)
            print(client.recv(1024).decode())  # status msg1

        elif inp == "2":
            client.send(inp.encode())
            print(client.recv(1024).decode())  # msg1
            file_name = input("Client: Enter file Name:")
            client.send(file_name.encode())  # file_name send
            file_type = type_assigner(file_name)
            received = client.recv(1024).decode()
            file_name, file_size = received.split(SEPARATOR)
            print("Master: Size of File", file_size, "bytes")
            time.sleep(5)
            client_receive(client, file_name, file_type)
            print(client.recv(1024).decode())  # status msg3

        elif inp == "3":
            client.send(inp.encode())
            print("Client: Closing Connection, Exiting...")
            try:
                client.close()
            except Exception as e:
                print(e)
            return False


# Test File: ./Client_Storage/Send_test.txt
# Recieve Text File: text.txt
# Test File: ./Client_Storage/download.jpg


if __name__ == '__main__':
    print("Client up and running")
    while client_driver():
        client_driver()
        server = ""
    # AESKey = ""
    # FLAG_READY = "Ready"
    # FLAG_QUIT = "quit"
    # # 10.1.236.227
    # # public key and private key
    # random = Random.new().read
    # RSAkey = RSA.generate(1024, random)
    # public = RSAkey.publickey().exportKey()
    # private = RSAkey.exportKey()
    #
    # tmpPub = hashlib.md5(public)
    # my_hash_public = tmpPub.hexdigest()

    # print("Client Closed Connection")
    # client = socket.socket()
    # client.connect(('10.113.7.17', 10002))
    # client_send(client, './Client_Storage/download.jpg', 'image')

