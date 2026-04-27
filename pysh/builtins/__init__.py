from .cd import builtin_cd as cd
from .echo import builtin_echo as echo
from .exit import builtin_exit as exit
from .sysinfo import builtin_sysinfo as sysinfo
from .download import builtin_download as download
from .procinfo import builtin_procinfo as procinfo
from .cat import builtin_cat as cat
from .head import builtin_head as head
from .wc import builtin_wc as wc
from .help import builtin_help as help
from .pwd import builtin_pwd as pwd


__all__ = [
    "cd",
    "echo",
    "exit",
    "sysinfo",
    "download",
    "procinfo",
    "cat",
    "head",
    "wc",
    "help",
    "pwd",
]
