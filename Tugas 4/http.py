import sys
import os
import os.path
import uuid
from glob import glob
from datetime import datetime
import urllib.parse

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}: {}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                return self.http_post(object_address, all_headers)
            elif method == 'DELETE':
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        thedir = './'

        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah Web Server Percobaan', dict())

        if object_address == '/list':
            daftar_file = os.listdir(thedir)
            isi = '\n'.join(daftar_file)
            return self.response(200, 'OK', isi, {'Content-type': 'text/plain'})

        if object_address == '/video':
            return self.response(302, 'Found', '', dict(location='https://youtu.be/katoxpnTf04'))

        if object_address == '/santai':
            return self.response(200, 'OK', 'Santai saja', dict())

        object_address = object_address[1:]  
        if not os.path.isfile(thedir + object_address):
            return self.response(404, 'Not Found', f'{object_address} tidak ditemukan', {})

        with open(thedir + object_address, 'rb') as fp:
            isi = fp.read()

        fext = os.path.splitext(thedir + object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')

        headers = {'Content-type': content_type}
        return self.response(200, 'OK', isi, headers)

    def http_post(self, object_address, headers):
        if object_address == '/upload':
            try:
                filename = None
                body_start = False
                body_lines = []

                for h in headers:
                    if h.lower().startswith('filename:'):
                        filename = h.split(':')[1].strip()
                    if body_start:
                        body_lines.append(h)
                    if h == '':
                        body_start = True

                if not filename:
                    return self.response(400, 'Bad Request', 'Filename header is required', {})

                filedata = '\n'.join(body_lines)

                with open(filename, 'w') as f:
                    f.write(filedata)

                return self.response(200, 'OK', f'{filename} uploaded successfully', {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e), {})
        else:
            return self.response(404, 'Not Found', '', {})

    def http_delete(self, object_address, headers):
        if object_address.startswith('/delete'):
            try:
                parsed = urllib.parse.urlparse(object_address)
                query = urllib.parse.parse_qs(parsed.query)
                filename = query.get('filename', [None])[0]

                if not filename:
                    return self.response(400, 'Bad Request', 'No filename provided', {})

                if not os.path.exists(filename):
                    return self.response(404, 'Not Found', f'File {filename} not found', {})

                os.remove(filename)
                return self.response(200, 'OK', f'{filename} deleted successfully', {'Content-type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e), {})
        else:
            return self.response(404, 'Not Found', '', {})


if __name__ == "__main__":
    httpserver = HttpServer()