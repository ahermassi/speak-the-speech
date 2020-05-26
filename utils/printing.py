from colorama import Fore, Style


def print_error(msg):
    print(Fore.RED + Style.BRIGHT + f"{msg}" + Style.RESET_ALL)


def print_notification(msg):
    print(Fore.GREEN + Style.BRIGHT + f"{msg}" + Style.RESET_ALL)


def print_blue_bold(msg):
    print(Fore.BLUE + Style.BRIGHT + f"{msg}" + Style.RESET_ALL)


def print_white(msg):
    print(Fore.WHITE + Style.NORMAL + f"{msg}" + Style.RESET_ALL)