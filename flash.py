import logging, colorlog
import subprocess, os
import threading
from queue import Queue, Empty
import time


# Logger Configuration
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

logger = colorlog.getLogger("Rshell Logger")
response = colorlog.getLogger("Console Response")
logger.addHandler(handler)
response.addHandler(handler)
logger.setLevel(logging.DEBUG)
response.setLevel(logging.INFO)

file_queue = Queue()


def consoleMonitor(rshell_process, file_queue, port):
    try:
        while True:
            line = rshell_process.stdout.readline().strip()
            if line:
                response.info(line)
                if line.startswith("Retrieving root directories ..."):
                    data_line = line.split()
                    for item in data_line:
                        if item.endswith(".py/"):
                            file_queue.put(item)
                if line.startswith(f"failed to access {port}"):
                    logger.critical(line)
            elif rshell_process.poll() is not None:
                logger.error("Rshell process terminated.")
                break
    except Exception as e:
        logger.error(f"Error in consoleMonitor: {e}")


def startShell(port):
    logger.debug("Attempting to open rshell connection...")
    try:
        rshell_process = subprocess.Popen(
            ['rshell', '-p', port],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        logger.debug("Rshell process started successfully")
        return rshell_process
    except FileNotFoundError:
        logger.debug("rshell executable not found. Is it installed and in PATH?")
    except subprocess.SubprocessError as e:
        logger.error(f"Error starting rshell: {e}")
    return None


def deleteFiles(rshell_process, file_queue):
    logger.debug("Initialising file deletion")

    while not file_queue.empty():
        try:
            file = file_queue.get(timeout=10)
            logger.debug(f"File to delete: {file}")
            if file.endswith('.py/'):
                file = file[:-1]
            command = f"rm /pyboard{file}\n"
            rshell_process.stdin.write(command)
            rshell_process.stdin.flush()
            logger.debug(f"Deleted file: {file}")
            time.sleep(2)
        except Empty:
            logger.warning("File queue is empty.")
            break
    logger.debug("The microcontroller board was erased successfully")


def uploadFiles(rshell_process):
    folder_path = "firmware"
    for filename in os.listdir(folder_path):
        command = f"cp firmware/{filename} /pyboard/{filename}\n"
        logger.debug(f'Uploading file: {filename}')
        rshell_process.stdin.write(command)
        rshell_process.stdin.flush()
        time.sleep(2)
    logger.debug("Files have been successfully uploaded")
    #runMain(rshell_process)

def runMain():
    pass

def flashDevice(port):
    rshell_process = startShell(port)
    if rshell_process:
        monitor_thread = threading.Thread(
            target=consoleMonitor, args=(rshell_process, file_queue, port), daemon=True)
        monitor_thread.start()

        logger.debug("Waiting for Python files...")

        start_time = time.time()
        timeout = 15

        while True:
            if not file_queue.empty():
                logger.debug("Files detected, proceeding with deletion.")
                break
            if time.time() - start_time > timeout:
                logger.warning("No files detected within the timeout period. Proceeding with upload.")
                break
            time.sleep(0.1)

        if not file_queue.empty():
            deleteFiles(rshell_process, file_queue)

        uploadFiles(rshell_process)


if __name__ == "__main__":
    flashDevice('COM7')

