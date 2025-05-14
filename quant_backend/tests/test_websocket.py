import unittest
from flask_socketio import SocketIO
from quant_backend.app import app, socketio

class TestWebSocket(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.socketio_client = socketio.test_client(app)

    def test_connect(self):
        self.assertTrue(self.socketio_client.is_connected())

    def test_disconnect(self):
        self.socketio_client.disconnect()
        self.assertFalse(self.socketio_client.is_connected())

    def test_client_event(self):
        test_data = {'message': 'test message'}
        self.socketio_client.emit('client_event', test_data)
        received = self.socketio_client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'server_response')
        self.assertEqual(received[0]['args'][0]['original_payload'], test_data)

if __name__ == '__main__':
    unittest.main() 