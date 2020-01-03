from src.networkguardian import ExamplePlugin, Platform


def main():
    plugins = [ExamplePlugin()]
    print(Platform.detect())

    for p in plugins:
        p.load(Platform.detect())

    print("STARTING SCANNING")

    for p in plugins:
        if p.supported:
            p.execute()
            print(f'Scanning with {p.name}')


if __name__ == '__main__':
    main()
