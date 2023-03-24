"""Enclave application."""
import socket
import json

ENCLAVE_PORT = 5000


def main():
    """Run the nitro enclave application."""
    # Bind and listen on vsock.
    vsock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)  # pylint:disable=no-member
    vsock.bind((socket.VMADDR_CID_ANY, ENCLAVE_PORT))  # pylint:disable=no-member
    vsock.listen()

    print('Listening...')

    while True:
        conn, _addr = vsock.accept()
        print('Received new connection')
        payload = conn.recv(4096)

        # Load the JSON data provided over vsock
        try:
            json_payload = json.loads(payload.decode())
        except Exception as exc: # pylint:disable=broad-except
            msg = f'Exception ({type(exc)}) while loading JSON data: {str(exc)}'
            content = {
                'success': False,
                'error': msg
            }
            conn.send(str.encode(json.dumps(content)))
            conn.close()
            continue

        content = {
            'success': True,
            'return_payload': json_payload
        }

        conn.send(str.encode(json.dumps(content)))
        conn.close()
        print('Closed connection')


if __name__ == '__main__':
    main()
