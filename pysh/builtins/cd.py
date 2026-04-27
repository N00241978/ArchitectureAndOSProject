import os


def builtin_cd(args):
    os.chdir(args[0])
