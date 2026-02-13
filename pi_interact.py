import serial


class Talker:
    TERMINATOR = '\r'.encode('UTF8')

    def __init__(self, timeout=1):
        self.serial = serial.Serial('COM3', 115200, timeout=timeout)
        self.send_to_LCD('Ready!')
        self.receive()

    def send(self, text: str):
        line = '%s\r\f' % text
        self.serial.write(line.encode('utf-8'))
        reply = self.receive()
        reply = reply.replace('>>> ', '')  # lines after first will be prefixed by a prompt
        if reply != text:  # the line should be echoed, so the result should match
            print('expected %s got %s' % (text, reply))

    def send_to_LCD(self, text: str):
        text = f"show_title('{text}')"
        line = '%s\r\f' % text
        self.serial.write(line.encode('utf-8'))
        reply = self.receive()
        reply = reply.replace('>>> ', '')  # lines after first will be prefixed by a prompt
        if reply != text:  # the line should be echoed, so the result should match
            print('expected %s got %s' % (text, reply))
        else:
            print('Successfully connected!')

    def receive(self) -> str:
        line = self.serial.read_until(self.TERMINATOR)
        return line.decode('UTF8').strip()

    def close(self):
        self.serial.close()