import socket
import logging
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    try:
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            data = connection.recv(1024)
            if not data:
                break
            buffer += data

        header_end = buffer.find(b"\r\n\r\n") + 4
        header_part = buffer[:header_end].decode()
        body_part = buffer[header_end:]

        lines = header_part.split("\r\n")
        content_length = 0
        for line in lines:
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())

        while len(body_part) < content_length:
            more_data = connection.recv(1024)
            if not more_data:
                break
            body_part += more_data

        full_request = header_part.encode() + body_part
        request_str = full_request.decode(errors='ignore')

        logging.warning("FULL REQUEST:\n" + request_str)

        hasil = httpserver.proses(request_str)
        hasil += b"\r\n\r\n"
        connection.sendall(hasil)
    except Exception as e:
        logging.warning(f"Error processing client: {e}")
    finally:
        connection.close()


def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(10)
    print("Server listening on port 8889...")

    with ProcessPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            jumlah = ['x' for i in the_clients if i.running()]
            print(f"Jumlah aktif: {len(jumlah)}")


def main():
    Server()

if __name__ == "__main__":
    main()
