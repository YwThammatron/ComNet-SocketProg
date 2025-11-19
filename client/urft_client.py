import socket
import sys
from datetime import datetime as dt

buf = 32768
timeout = 8
sep = '/||/'

def start_client():

    if len(sys.argv) < 4:
        print("python urft_client.py <file_path> <server_ip> <server_port>")
        sys.exit(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    server_address = (sys.argv[2], int(sys.argv[3]))
    client_socket.setblocking(True)

    current_ack = 0

    with open(sys.argv[1], 'rb') as file:
        file_data = file.read()
        print("Read file")

    file_size = len(file_data)

    while 1:
        sender_time = dt.now()
        # Send the file name as a UTF-8 encoded header
        packet = f'-2{sep}{sys.argv[1]}'.encode('utf-8')
        client_socket.sendto(packet, server_address)
        try:
            ack_data, server = client_socket.recvfrom(buf) 
            ack, time = ack_data.decode('utf-8').split(sep)  # This is for the ACK response, which is text-based
            if ack != "ACK": continue

            time = dt.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
            rtt = (time.microsecond - sender_time.microsecond) * 0.000001
            client_socket.settimeout(timeout)
            print(f"start sending data with RTT: {rtt}")
            break

        except socket.timeout:
            print("--Timeout Retransmission--")

    while 1:
        if current_ack == -1: break

        if current_ack >= file_size:
            # Send FIN packet when all data is sent
            packet = f'-1{sep}FIN'.encode('utf-8')
            client_socket.sendto(packet, server_address)
            print(f"Sending FIN: {seq}")

        print(f"Sending SEQ: {current_ack} - {file_size - buf}")
        for seq in range(current_ack, file_size, buf):  # send many at the same time
            chunk = file_data[seq:seq + buf]
            # Send packet with sequence number and binary chunk (no encoding for chunk)
            packet = f"{seq}{sep}".encode('utf-8') + chunk
            client_socket.sendto(packet, server_address)

        try:
            while 1:
                ack_data, server = client_socket.recvfrom(40)  # Header size
                ack_parts = ack_data.decode('utf-8').split(sep)  # Header part decoded as UTF-8

                flag = ack_parts[0]
                current_ack = int(ack_parts[1])
                print(f'Furthest {flag}: {current_ack}')

                if flag == 'FIN':
                    break

        except socket.timeout:
            print("--Timeout Retransmission--")

    print("File sent successfully!")
    client_socket.close()

if __name__ == "__main__":
    start_client()
