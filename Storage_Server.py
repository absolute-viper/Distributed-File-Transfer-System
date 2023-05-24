import socket
import os
import time

master_server_ip = ''
master_server_port = 10001
storage_directory = './Server_Storage/'
SEPARATOR = "<sep>"


def file_name_retriever(file_path):
    return file_path.split('/')[-1]


def storage_send(storage, file_name):
    path = os.path.join(storage_directory + file_name)
    file_size = os.path.getsize(path)
    storage.send(f"{file_name}{SEPARATOR}{file_size}".encode())
    time.sleep(2)
    file = open(path, "r")
    data = file.read()
    storage.send(data.encode())
    file.close()

    """ Uncomment the below code for IMAGE Sever"""
    """ Comment the above lines while doing so"""
    # For IMAGE SERVER (image sending)
    # file = open(path, 'rb')
    # image_data = file.read(2048)
    # while image_data:
    #     client.send(image_data)
    #     image_data = file.read(2048)
    # file.close()


def storage_receive(storage, file_name):
    path = os.path.join(storage_directory + file_name)
    file = open(path, "w")
    data = storage.recv(1024).decode()
    file.write(data)
    file.close()

    """ Uncomment the below code for IMAGE Sever"""
    """ Comment the above lines while doing so"""
    # file = open(path, "wb")
    # image_chunk = storage.recv(2048)  # stream-based protocol
    # while image_chunk:
    #     file.write(image_chunk)
    #     image_chunk = storage.recv(2048)
    # file.close()


def storage_server_driver():
    """ Connecting to the Master Server """
    storage = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storage.bind((master_server_ip, master_server_port))
    storage.listen(5)
    master, addr = storage.accept()
    print("Connected to Master Server {0}".format(addr))

    while True:
        inp = master.recv(1024).decode()
        if inp == "a":
            print("Server: Uploading to Self")
            try:
                received = master.recv(1024).decode()
                file_name, file_size = received.split(SEPARATOR)
                print("Master: File being Uploaded:", file_name)
                print("Master: Size of the file:", file_size)
                storage_receive(master, file_name)
                print("File Upload Completed Successfully")
            except Exception as e:
                print("File Upload Error", e)

        elif inp == "b":
            file_name = storage.recv(1024).decode()
            print("Master: File being requested:", file_name)
            file_path = os.path.join(storage_directory, file_name)
            try:
                os.path.exists(file_path)
                str1 = "Server: File Exists in Location"
                master.send(str1.encode())
                try:
                    storage_send(master, file_name)
                    print("Server: File Download to Master Completed Successfully")
                except Exception as e:
                    print("Server: File Download to Master Error", e)

            except FileExistsError:
                str1 = "Server: File Not present on Server"
                master.send(str1.encode())
            print("Server: Downloading to Master-Client")


if __name__ == '__main__':
    print("Storage Server {type} up and running")
    while storage_server_driver():
        storage_server_driver()
    print("Storage Server type {name} closed Connection")
    # Server implementation
