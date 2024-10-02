import socket
import argparse
import logging
import base64
from datetime import datetime


class CameraControl:
    """
    A class to control and interact with a network camera.

    This class provides methods to trigger the camera, acquire images,
    and send commands over a network connection.
    """

    def __init__(self, host: str, control_port: int, results_port: int):
        """
        Initialize the CameraControl instance.

        Args:
            host (str): The IP address or hostname of the camera.
            control_port (int): The port number for sending control commands.
            results_port (int): The port number for receiving results.
        """
        self.host = host
        self.control_port = control_port
        self.results_port = results_port

        # Configure logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def acquire_image(self) -> None:
        """
        Trigger the camera to capture an image and save it.

        This method sends a trigger command, retrieves the image data,
        and saves it to a file.
        """
        self.logger.info("Acquiring image from camera")

        # Trigger the camera
        self.trigger()

        # Request the image data
        response = self.send_command("getresultimage\r\n")

        if b"/9j/" in response:  # Check for JPEG image data
            self._process_image_data(response)
        else:
            self.logger.warning("No image data found in the response")

    def _process_image_data(self, response: bytes) -> None:
        """
        Process the image data from the camera response.

        Args:
            response (bytes): The raw response from the camera.
        """
        try:
            base64_data = response.split(b"/9j/")[1]
            image_data = base64.b64decode(b"/9j/" + base64_data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"output_image_{timestamp}.jpg"
            image_path = (
                f"./images/{image_filename}"  # Save in a local 'images' directory
            )

            self.save_image_data(image_data, image_path)
            self.logger.info(f"Image saved successfully: {image_filename}")
        except Exception as e:
            self.logger.error(f"Error processing image data: {e}")

    def send_command(self, command: str) -> bytes:
        """
        Send a command to the camera and return the response.

        Args:
            command (str): The command to send to the camera.

        Returns:
            bytes: The raw response from the camera.

        Raises:
            ConnectionError: If unable to connect to the camera.
        """
        self.logger.info(f"Sending command: {command.strip()}")

        # Send command to control port
        self._send_to_socket(self.host, self.control_port, command.encode("utf-8"))

        # Receive response from results port
        return self._receive_from_socket(self.host, self.results_port)

    def _send_to_socket(self, host: str, port: int, data: bytes) -> None:
        """
        Send data to a specific host and port using a socket.

        Args:
            host (str): The target host.
            port (int): The target port.
            data (bytes): The data to send.

        Raises:
            ConnectionError: If unable to connect or send data.
        """
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(data)
        except (socket.timeout, ConnectionRefusedError) as e:
            raise ConnectionError(f"Failed to send data to {host}:{port}. Error: {e}")

    def _receive_from_socket(self, host: str, port: int) -> bytes:
        """
        Receive data from a specific host and port using a socket.

        Args:
            host (str): The host to receive from.
            port (int): The port to receive from.

        Returns:
            bytes: The received data.

        Raises:
            ConnectionError: If unable to connect or receive data.
        """
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                response = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                return response
        except (socket.timeout, ConnectionRefusedError) as e:
            raise ConnectionError(
                f"Failed to receive data from {host}:{port}. Error: {e}"
            )

    @staticmethod
    def save_image_data(image_data: bytes, image_path: str) -> None:
        """
        Save image data to a file.

        Args:
            image_data (bytes): The raw image data.
            image_path (str): The path where the image should be saved.

        Raises:
            IOError: If unable to write the image file.
        """
        try:
            with open(image_path, "wb") as f:
                f.write(image_data)
        except IOError as e:
            raise IOError(f"Failed to save image to {image_path}. Error: {e}")

    def trigger(self) -> None:
        """
        Trigger the camera to capture an image.
        """
        self.logger.info("Triggering camera")
        self.send_command("TRIGGER\r\n")


def main():
    """
    Main function to handle command-line arguments and control the camera.
    """
    parser = argparse.ArgumentParser(description="Control a network camera.")
    parser.add_argument(
        "--host", type=str, default="192.168.1.200", help="Camera host address"
    )
    parser.add_argument("--control-port", type=int, default=107, help="Control port")
    parser.add_argument("--results-port", type=int, default=25250, help="Results port")
    parser.add_argument(
        "-t", "--trigger", action="store_true", help="Trigger the camera"
    )
    parser.add_argument(
        "-a", "--acquire", action="store_true", help="Acquire an image from the camera"
    )

    args = parser.parse_args()

    try:
        camera = CameraControl(args.host, args.control_port, args.results_port)

        if args.trigger:
            camera.trigger()
        elif args.acquire:
            camera.acquire_image()
        else:
            print("Please specify either --trigger or --acquire")
    except ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
