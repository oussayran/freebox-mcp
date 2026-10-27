import unittest
from unittest.mock import patch
import server

class RemoteTests(unittest.TestCase):
    def test_invalid_key_never_calls_network(self):
        with patch('server.request') as request:
            with self.assertRaises(ValueError):
                server.send('invalid')
            request.assert_not_called()

    def test_missing_code_never_calls_network(self):
        with patch('server.config', return_value=('hd1.freebox.fr', '')), patch('server.request') as request:
            with self.assertRaises(ValueError):
                server.send('home')
            request.assert_not_called()

    def test_rejection_does_not_leak_code(self):
        with patch('server.config', return_value=('hd1.freebox.fr', '12345678')), patch('server.request', return_value=403):
            with self.assertRaises(RuntimeError) as error:
                server.send('home')
            self.assertNotIn('12345678', str(error.exception))

    def test_long_press_and_success(self):
        with patch('server.config', return_value=('hd1.freebox.fr', '12345678')), patch('server.request', return_value=200) as request:
            self.assertTrue(server.send('1', True)['accepted'])
            self.assertEqual(request.call_args.args[0]['long'], 'true')

if __name__ == '__main__':
    unittest.main()
