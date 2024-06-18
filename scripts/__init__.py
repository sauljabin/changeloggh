import shlex
import subprocess

from rich.console import Console


class CommandProcessor:
    def __init__(self, commands):
        self.commands = commands

    def run(self):
        console = Console()

        for name, command in self.commands.items():
            console.print()
            console.print(f"[bold blue]{name.lower()}:")
            console.print(f"[bold yellow]{command}[/]")
            command_split = shlex.split(command)
            result = subprocess.run(command_split)
            if result.returncode:
                raise Exception(
                    f"\n[bold red]Error:exclamation:[/] in [bold blue]{name} ([bold"
                    f" yellow]{command}[/])[/]"
                )


if __name__ == "__main__":
    test_commands = {"list files": "ls .", "testing echo": "echo 'hello world'"}
    command_processor = CommandProcessor(test_commands)
    command_processor.run()
