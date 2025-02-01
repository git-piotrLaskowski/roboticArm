# Micro Python Touch Robot
The program manages files on a microcontroller connected via `rshell`.  

# **Functionality**:
1. **Device connection** - Starts `rshell` on the specified serial port.  
2. **Console monitoring** - Reads `rshell` responses and detects `.py` files to be deleted.  
3. **Delete files** - Automatically deletes found `.py` scripts from the device.  
4. **Import new files** - Copies the contents of the `firmware` folder to the microcontroller.  
5. **Error handling and logging** - Uses `colorlog` to log events transparently.  

The program runs with the `COM7` port, but can be adapted to other devices.

## 1. Erasing board:

Remember to change port (COM7) to actual one on your PC

```shell
$ esptool.py --port COM7 erase_flash
```

## 2. Flashing board:


```shell
$ esptool.py --port COM7 write_flash -z 0x1000 ESP32_GENERIC-20241025-v1.24.0.bin
```

## 2. Flash firmware

To flash firmware just run 
```shell
$ python flash_ESP.py
```
via python configuration. With micropython plugin it may not work. Remember to check COM port.
    
