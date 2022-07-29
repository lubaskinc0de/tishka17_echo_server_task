import socket
from select import select
import logging
from typing import Type

class Logger:
    '''The default logger for socket-server.'''

    logging_level: str = logging.INFO
    logging_time_format: str = '%Y-%m-%d'

    _log_format: str = f'[%(asctime)s] %(levelname)s [%(filename)s at %(lineno)d line] - %(message)s'

    @classmethod
    def get_stream_handler(cls: Type['Logger']) -> 'logging.StreamHandler':
        '''Get stream handler for logger -> logging.StreamHandler().'''
        stream_handler: Type['logging.StreamHandler'] = logging.StreamHandler()
        stream_handler.setLevel(cls.logging_level)
        stream_handler.setFormatter(logging.Formatter(cls._log_format, cls.logging_time_format))
        return stream_handler
    
    @classmethod
    def get_logger(cls: 'Logger', name: str) -> 'logging.Logger':
        '''Get logger -> logging.Logger'''
        logger: logging.Logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(cls.get_stream_handler())
        return logger


class SocketServer:
    '''The socket-server'''
    logger = Logger.get_logger(__name__)

    def __init__(
        self: 'SocketServer', socket_protocol = socket.AF_INET, socket_stream = socket.SOCK_STREAM,
        host: str='127.0.0.1', port: int = 5000,
        ) -> None:
        self._protocol = socket_protocol
        self._stream = socket_stream
        self.host: str = host
        self.port: int = port
        self.sockets: list = []
    
    def _get_server_socket(self: 'SocketServer') -> 'socket.socket':
        '''Get server socket -> socket.socket'''
        server_socket = socket.socket(self._protocol, self._stream)
        return server_socket
    
    def runserver(self: 'SocketServer') -> None:
        '''Run server'''
        server_socket = self._get_server_socket()
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        self.sockets.append(server_socket)
        self.logger.info('Server configured, running event loop..')
        self._run_event_loop(server_socket)

    def _run_event_loop(self: 'SocketServer', server_socket: 'socket.socket') -> None:
        '''Run event loop'''
        self.logger.info('Event loop is run.')
        self.logger.info(f'Server is now running at {self.host}:{self.port}')
        while True:
            ready_sockets, _, _ = select(self.sockets, [], [])
            for socket in ready_sockets:
                if socket is server_socket:
                    self._handle_request(socket)
                else:
                    self._handle_response(socket)
    
    def _handle_request(self: 'SocketServer', server_socket: 'socket.socket') -> None:
        '''Accept request'''
        client_socket, client_addr = server_socket.accept()
        self.logger.info(f'Accept connection from {client_addr}.')
        self.sockets.append(client_socket)

    def _handle_response(self: 'SocketServer', client_socket: 'socket.socket') -> None:
        '''Send response'''
        try:
            request: bytes = client_socket.recv(1024)
            self.logger.info('Accept request.')

        except ConnectionResetError:
            request = None
            self.logger.info('Client connection is reset.')

        if request:
            response: bytes = request
            client_socket.send(response)
            self.logger.info('Response is successfully send.')
        else:
            self.sockets.remove(client_socket)
            client_socket.close()

s = SocketServer()
s.runserver()
