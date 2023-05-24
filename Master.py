import socket
import os
import time

client_ip, client_port = '', 9000 # Ritik (Client)

# storage1_ip, storage1_port = '127.0.0.1', 10001  # LocalHost Test
storage1_ip, storage1_port = "10.113.6.209", 10001  # Purushoath (Document)
storage2_ip, storage2_port = "10.113.7.17", 10002  # Akshay (Image)
storage3_ip, storage3_port = "10.113.6.121", 10003  # Undecided
storage_directory = './Master_Storage/'
SEPARATOR = "<sep>"

extensions = {
    "jpg": "images", "png": "images", "ico": "images", "gif": "images", "svg": "images",
    "mp3": "audio", "wav": "audio",
    "mp4": "video", "m3u8": "video", "webm": "video", "ts": "video",
    "pdf": "document", "xlsx": "document", "csv": "document", "docx": "document", "txt": "document",
    "pptx": "document", "ppt": "document"
}


def file_name_retriever(file_path):
    return file_path.split('/')[-1]


def connection_maker(connect_ip, connect_port):
    s = socket.socket()
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((connect_ip, connect_port))
        s.settimeout(None)
        print("Connected to Server {0}".format(connect_ip))
    except Exception as e:
        print("Could not connect to {0} {1}".format(connect_ip, e))
    return s


def server_assigner(file_loc, master_s1, master_s2, master_s3):  # Assigns server to the file being uploaded
    file_name = file_loc.split('/')[-1]
    ext = file_name.split('.')[-1]
    file_type = ""
    if ext in extensions:
        file_type = extensions[ext]
    if file_type == 'document':
        return master_s1, 'document'
    elif file_type == 'images':
        return master_s2, 'image'
    elif file_type == 'audio' or file_type == 'video':
        return master_s3, 'audio/video'


def master_local_uploader(master, file_path, file_type):
    file_name = file_name_retriever(file_path)
    path = os.path.join(storage_directory, file_name)
    file_size = os.path.getsize(path)
    master.send(f"{file_name}{SEPARATOR}{file_size}".encode())
    if file_type == 'document':
        time.sleep(2)
        file = open(path, "r")
        data = file.read()
        master.send(data.encode())
        file.close()

    elif file_type == 'image':
        time.sleep(2)
        file = open(path, 'rb')
        image_data = file.read(2048)
        while image_data:
            master.send(image_data)
            image_data = file.read(2048)
        file.close()


def master_local_downloader(master, file_name, file_type):
    path = os.path.join(storage_directory, file_name)
    if file_type == 'document':
        file = open(path, "w")
        data = master.recv(1024).decode()
        file.write(data)
        file.close()

    elif file_type == 'image':
        file = open(path, "wb")
        time.sleep(2)
        image_chunk = master.recv(2048)  # stream-based protocol
        while True:
            print(len(image_chunk))
            file.write(image_chunk)
            image_chunk = master.recv(2048)
            if master.recv(2048) == b"":
                break

        file.close()
        print("Uploaded Successfully")


def master_driver():
    """ Connecting to the Client """
    master_c = socket.socket()
    master_c.bind((client_ip, client_port))
    master_c.listen(5)
    client, addr = master_c.accept()
    print("Connected to Client {0}".format(addr[0]))

    """ Connecting to the Storage Server 1 """
    master_s1 = connection_maker(storage1_ip, storage1_port)

    """ Connecting to the Storage Server 1 """
    master_s2 = connection_maker(storage2_ip, storage2_port)

    """ Connecting to the Storage Server 1 """
    master_s3 = connection_maker(storage3_ip, storage3_port)

    while True:
        str1 = "Master: Select an option:\n" \
               "Master: 1. Upload File \n\t\t2. Download File \n\t\t3. Exit"
        time.sleep(2)
        client.send(str1.encode())
        inp = client.recv(1024).decode()
        print(inp)
        if inp == "1":
            str1_inp1 = "***** File Upload Module *****\n" \
                        "Master: Enter complete path of the File"
            client.send(str1_inp1.encode())  # msg1
            received = client.recv(1024).decode()
            print(received)
            file_name, file_size = received.split(SEPARATOR)
            server_obj, file_type = server_assigner(file_name, master_s1, master_s2, master_s3)
            print("Client: Name of the File to be uploaded:", file_name)
            print("Client: Size of File", file_size, "bytes")
            master_local_downloader(client, file_name, file_type)
            print("Master: Upload server details:", server_obj)
            try:
                server_obj.send("a".encode())
                print("Requesting Upload to Server...")
                time.sleep(2)
                master_local_uploader(server_obj, file_name, file_type)
                time.sleep(2)
                os.remove(storage_directory + file_name)
                str3_inp1 = "File Upload Completed Successfully"
            except Exception as e:
                str3_inp1 = "Error While Uploading: " + str(e)
            client.send(str3_inp1.encode())
            time.sleep(2)
            print(str3_inp1)

        elif inp == "2":
            str1_inp2 = "***** File Download Module *****\n" \
                        "Master: Enter File name with extension"
            client.send(str1_inp2.encode())  # msg1
            file_name = client.recv(1024).decode()
            print("Client: Name of the File to be downloaded:", file_name)
            file_path = os.path.join(storage_directory, file_name)
            server_obj, file_type= server_assigner(file_path, master_s1, master_s2, master_s3)
            print("Master: Download server details:", server_obj)
            try:
                server_obj.send("b".encode())
                time.sleep(2)
                print("Requesting Download from Server...")
                server_obj.send(file_name.encode())
                print("File name sent",file_name)
                server_obj.recv(1024).decode()  # msg File (Present or not)
                time.sleep(2)
                received = server_obj.recv(1024).decode()
                file_name, file_size = received.split(SEPARATOR)
                print("Server: Name of the File being downloaded:", file_name)
                print("Server: Size of File", file_size, "bytes")
                master_local_downloader(server_obj, file_name, file_type)
                print("Master: Local Download Complete")
                master_local_uploader(client, file_path, file_type)
                os.remove(file_path)
                str3_inp2 = "Master: File Downloaded Successfully"
            except Exception as e:
                str3_inp2 = "Error While Downloading: " + str(e)
            client.send(str3_inp2.encode())
            time.sleep(2)
            print(str3_inp2)



        elif inp == "3":
            print("Master: Closing Connection, Exiting...")
            try:
                client.close()
            except Exception as e:
                print(e)
            return False


# Actual Driver Code
if __name__ == "__main__":
    print("Master Server up and running")
    while master_driver():
        master_driver()
    print("Master Server Closed Connection")

# # Test Driver Code
# if __name__ == "__main__":
#
#     master_s1 = socket.socket()
#     master_s1.settimeout(5)
#     master_s1.bind((client_ip, client_port))
#     master_s1.listen(5)
#     client_ip, addr = master_s1.accept()
#     master_s1.settimeout(None)
#     print("Connected to Server {0}".format(client_ip))
#     master_local_downloader(client_ip, 'recvd.jpg', 'image')

#     color_print("\n[!] One client is trying to connect...", color="green", bold=True)
#     # get client public key and the hash of it
#     clientPH = client.recv(2048)
#     split = clientPH.split(":")
#     tmpClientPublic = split[0]
#     clientPublicHash = split[1]
#     color_print("\n[!] Anonymous client's public key\n",color="blue")
#     print tmpClientPublic
#     tmpClientPublic = tmpClientPublic.replace("\r\n", '')
#     clientPublicHash = clientPublicHash.replace("\r\n", '')
#     tmpHashObject = hashlib.md5(tmpClientPublic)
#     tmpHash = tmpHashObject.hexdigest()
#
#     if tmpHash == clientPublicHash:
#         # sending public key,encrypted eight byte ,hash of eight byte and server public key hash
#         color_print("\n[!] Anonymous client's public key and public key hash matched\n", color="blue")
#         clientPublic = RSA.importKey(tmpClientPublic)
#         fSend = eightByte + ":" + session + ":" + my_hash_public
#         fSend = clientPublic.encrypt(fSend, None)
#         client.send(str(fSend) + ":" + public)

