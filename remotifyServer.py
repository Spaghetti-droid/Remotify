import remotifyCommon as common

import argparse
import asyncio
import logging
import socket
from websockets.asyncio.server import serve
from pynput.keyboard import Key, Controller

logger = logging.getLogger(__name__)
keyboard = Controller()

def initArgParser() -> argparse.Namespace:
    """Defines the arguments that the program can use

    Returns:
        argparse.Namespace: The argument values the user specified to the application
    """
    parser = argparse.ArgumentParser(prog="remotifyServer.py", 
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=f'''\
Start a remotify server, which listens for single-character commands to execute. {common.SERVER_COMMAND_DESCRIPTION}
''')
    return parser.parse_args()

async def main():  
    logging.basicConfig(filename='remotifyServer.log', level=logging.DEBUG)
    initArgParser()
    logger.info("Server starting up")
    async with serve(listen, "", common.DEFAULT_PORT):
        hostIdMessage = f'Listening on host: {socket.gethostname()}'
        print(hostIdMessage)
        logger.info(hostIdMessage)
        await asyncio.get_running_loop().create_future() 

async def listen(websocket):
    """Listen for commands on websocket
    Args:
        websocket
    """
    async for message in websocket:
        logger.debug(f"Recieved input:'{message}'")
        literalKeys = False
        for c in message:
            # ! means interpret the rest as character key presses
            if not literalKeys and c == '!':
                literalKeys = True
                continue
                
            if literalKeys:
                key = c
            else:
                key = getNonCharKey(c)
                
            if key:
                keyboard.press(key)
                keyboard.release(key)
        
def getNonCharKey(c: str) -> Key:
    """Convert c into a media control Key
    Args:
        c (str): A character representing a media control operation
    Returns:
        Key: The key press that accomplishes the operation
    """
    match c:
        case 'p':
            return Key.media_play_pause
        case 'n':
            return Key.media_next
        case 'b':
            return Key.media_previous
        case 'u':
            return Key.media_volume_up
        case 'd':
            return Key.media_volume_down
        case 'm':
            return Key.media_volume_mute
        case '>':
            # Common +5s key
            return Key.right
        case '<':
            # Common -5s key
            return Key.left
        case '^':
            return Key.up
        case 'v':
            return Key.down
        case 'e':
            return Key.enter
        case _:
            logger.warning(f"Non-literal input not recognised: '{c}'")
            return None
        

if __name__ == "__main__":
    asyncio.run(main())