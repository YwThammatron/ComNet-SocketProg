import socket
import sys
import os
import time
from datetime import datetime as dt

buf = 32768
timeout = 30
sep = '/||/'

def start_server():

    if len(sys.argv) < 3:
        print("python urft_server.py <server_ip> <server_port>")
        sys.exit(1)

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (sys.argv[1], int(sys.argv[2]))
    server_socket.bind(server_address)
    server_socket.settimeout(timeout)

    file_name = ''
    file_data = bytearray()  # Use bytearray to accumulate binary data
    expected_seq = 0
    wndw = {}

    print("READY!")
    while 1:
        try:
            data, client_address = server_socket.recvfrom(buf + 20)

            # Handle the header part (UTF-8 encoded part)
            sep_pos = data.find(sep.encode('utf-8'))
            if sep_pos == -1:
                print("Invalid packet received. No separator found.")
                continue

            header = data[:sep_pos]  # This is the header part (sequence number, filename)
            payload = data[sep_pos + len(sep):]  # This is the binary payload

            # Decode the header (it's a UTF-8 encoded string with sequence number and filename)
            packet_parts = header.decode('utf-8').split(sep)

            seq = int(packet_parts[0])
            print(f"receiving SEQ: {seq} expect: {expected_seq}")

            if seq == -1:  # End signal
                print("Done!")
                print(len(file_data))
                packet = f'FIN{sep}{seq}'.encode('utf-8')
                server_socket.sendto(packet, client_address)
                break

            if seq == -2:  # Initial file name packet
                file_name = payload.decode('utf-8')  # File name is sent as a UTF-8 string
                server_socket.sendto(f"ACK{sep}{dt.now()}".encode('utf-8'), client_address)
                print("Got file name")
                continue

            # Add the binary payload to the window
            wndw[seq] = payload

            # Write the received binary data in the correct order
            while expected_seq in wndw.keys():
                file_data.extend(wndw[expected_seq])  # Add binary data to the file
                expected_seq += buf

            print(len(file_data))
            server_socket.sendto(f"ACK{sep}{expected_seq}".encode('utf-8'), client_address)
            print(f"sending ACK: {expected_seq}")

        except socket.timeout:
            print("Client is gone")
            break

    server_socket.close()

    file_name = f"./receive_file.bin"

    # Save the received file as binary data
    with open(file_name, "wb") as file:
        file.write(file_data)  # Write the binary data directly to the file

    print(f"File saved as: {file_name}")

if __name__ == "__main__":
    start_server()
