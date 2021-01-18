import xmlrpc.server
import cv2


def take_photo():
    cap = cv2.VideoCapture(1)
    success, image = cap.read()
    cap.release()
    if success:
        return image.tolist()
    else:
        raise RuntimeError('Failed to take photo')


if __name__ == '__main__':
    with xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 8000)) as server:
        server.register_function(take_photo)
        server.serve_forever()
