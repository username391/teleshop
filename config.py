import os
import toml
import pathlib

CURRENT_PATH = pathlib.Path(__file__).parent.resolve()

with open(os.path.join(CURRENT_PATH, 'config.toml')) as f:
    CONFIG = toml.load(f)

YOOMONEY_TOKEN = '410014713283544.96D0221DA659CDE11302588298DDEC5BA9CA67EFE3E4ED65D89BD5217D2E6475C8B4CBF81F5A63CC4D318A081E18D0FD95401E1EAA85870000901868CEB5CF17D903B2AA6BBFC1951A7CAB22470EEEF35C379478EBAA6F4D6EFF3B3AFD7B08A7CE8F6AFBAD2DDE10962C51A3E01FB7F08EB51D4C40D875C92D98AE4292B5D9E6'
RECIEVER = '410014713283544'
