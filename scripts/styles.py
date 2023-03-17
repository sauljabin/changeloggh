from scripts import CommandProcessor


def main():
    init_commands = {
        "black": "poetry run black . --preview",
        "ruff": "poetry run ruff . --fix",
    }
    command_processor = CommandProcessor(init_commands)
    command_processor.run()


if __name__ == "__main__":
    main()
