class OptionPicker:
    def __init__(self, text: str):
        self.__text = text
        self.__count: int = 0
        self.__is_default_set: bool = False
        self.__options: dict = {}

    def set_option(
        self,
        text: str,
        action,
        is_default: bool = False,
    ):
        self.__count += 1
        self.__options[self.__count] = [text, action, is_default]

    def __run(self, input_prompt, default=False):
        if self.__is_default_set is True and default is True:
            raise ValueError("Only one default option is allowed.")
        elif self.__is_default_set is False and default is True:
            self.__is_default_set = True

        print(self.__text)
        for key, val in self.__options.items():
            print(f"\t{key}. {val[0]}")

        try:
            take_input = int(input(input_prompt))

            if take_input in self.__options:
                self.__options[take_input][1]()

        except ValueError:
            if self.__is_default_set is True:
                print("Invalid option. Selecting the default option")
                for key, val in self.__options.items():
                    if val[2] is True:
                        self.__options[key][1]()
            else:
                print("Invalid option. Select a correct option")

                take_input = int(input(input_prompt))

                if take_input in self.__options:
                    self.__options[take_input][1]()

    def run(self, loop_count, input_prompt=">> "):
        for _ in range(loop_count):
            self.__run(input_prompt)

    def run_once(self, input_prompt=">> "):
        self.__run(input_prompt)

    def run_forever(self, input_prompt=">> ", default=False):
        while True:
            self.__run(input_prompt, default)
