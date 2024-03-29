import argparse
import linecache
import os
import random
import string
from os.path import expanduser
from os.path import expandvars

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"


def print_warning(message):
    """

    :param message: The message to be displayed

    """
    print(f"{RED}Warning: {message}{RESET}")


def print_info(message):
    """

    :param message: The message to be displayed

    """
    print(f"{YELLOW}Info: {message}{RESET}")


def print_success(message):
    """

    :param message: The message to be displayed

    """
    print(f"{GREEN}Success: {message}{RESET}")


def choose_word(punctuations=False, words_file="words.txt"):
    """

    :param punctuations: Default value = False)
    :param words_file: Default value = "words.txt")

    """
    try:
        lines = 0
        with open(words_file) as f:
            for _ in f:
                lines = lines + 1

        line_number = random.randint(1, lines)
        word = linecache.getline(words_file, line_number).strip(" \n\t\r")
        print(words_file)

        # Remove any punctuations to make the game less challenging (default)
        if not punctuations:
            word = word.translate(str.maketrans("", "", string.punctuation))

        return word
    except FileNotFoundError:
        print_warning(f"Error: {words_file} file not found.")
        exit(1)


def display_word(word, guessed_letters):
    """

    :param word: The secret to be displayed
    :param guessed_letters: The user input

    """
    display = ""
    for letter in word:
        if letter in guessed_letters:
            display += letter
        else:
            display += "_"
    return display


def hangman(punctuations, words_file, caseSensitive):
    """

    :param punctuations: Choose if punctuations should be removed or not
    :param words_file: Choose which file to get the files from
    :param caseSensitive: Choose if the input (and secret word) should be case insensitive or not

    """
    secret_word = choose_word(punctuations, words_file)
    unCasedSecret = secret_word
    guessed_letters = []
    attempts = random.randint(3, 9)

    secret_word = secret_word.lower()
    while attempts > 0:
        current_display = display_word(secret_word, guessed_letters)
        print("Current word:", current_display)
        print("Guessed letters:", guessed_letters)
        print("Attempts left:", attempts)

        guess = input("Guess a letter: ").lower()
        if not caseSensitive:
            guess = guess.lower()

        if guess.isalpha() and len(guess) == 1:
            if guess in guessed_letters:
                print_info("You've already guessed that letter. Try again.")
            elif guess in secret_word:
                print_success("Good guess!")
                guessed_letters.append(guess)
            else:
                print_warning("Incorrect guess.")
                attempts -= 1
                guessed_letters.append(guess)
        else:
            print("Please enter a valid single letter.")

        if "_" not in display_word(secret_word, guessed_letters):
            return True, unCasedSecret

    return False, unCasedSecret


def file_on_line(directory=os.path.expanduser("~")) -> str:
    """

    :param directory: Default value = os.path.expanduser("~"))

    """
    directory = os.path.abspath(directory)
    while True:
        try:
            files = os.listdir(directory)

            if not files:
                return ""

            selected_file = random.choice(files)
            selected_path = os.path.join(directory, selected_file)

            if os.path.isfile(selected_path):
                return selected_path

            if os.path.isdir(selected_path):
                directory = selected_path
            else:
                return ""
        except PermissionError:
            print_warning(
                "Error: Permission denied while accessing the directory.")
            exit(1)


# Use with caution!
def hang_the_file(filelocation):
    """

    :param filelocation: The path where the file is stored

    """
    try:
        os.remove(filelocation)
        print(f"Hanged {filelocation}!")
    except PermissionError:
        print_warning(f"Error: Permission denied for {filelocation}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="HangFile is a fun game that hangs your file if you lose")
    parser.add_argument(
        "-p",
        "--punctuation",
        default=False,
        action="store_true",
        help="Don't remove punctuations in the words",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="words.txt",
        help="Specify a file where words should be chosen from",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=f"{expanduser('~')}",
        help="Specify where the hang file(s) should be picked from",
    )
    parser.add_argument(
        "-r",
        "--remove",
        default=False,
        action="store_true",
        help="Remove/Hang the file (Permanent data loss)",
    )
    parser.add_argument(
        "-c",
        "--case",
        default=False,
        action="store_true",
        help="Don't make the game case insensitive",
    )

    args = parser.parse_args()

    if args.file and not os.path.isfile(args.file):
        print_warning(f"Error: Specified word file '{args.file}' not found.")
        exit(1)

    if args.directory and not os.path.isdir(expandvars(args.directory)):
        print_warning((
            f"Error: Specified directory '{expandvars(args.directory)}' not found"
        ))
        exit(1)

    hang_file = file_on_line(expandvars(args.directory))

    print_info(
        "Welcome to HangFile! In this game, the selected file will be 'hanged' if you lose."
    )
    print_info(f"Remember, '{hang_file}' will be hanged if you lose!")

    res, secret = hangman(args.punctuation, args.file, args.case)
    if res:
        print_success(
            f"You got it! '{hang_file}' {secret} is spared from the rope!")
    else:
        print_warning(
            f"Sorry to announce that the word was '{secret}' and '{hang_file}' will face the rope!"
        )
        if args.remove:
            hang_the_file(hang_file)
