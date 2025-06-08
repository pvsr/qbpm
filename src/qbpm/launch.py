import shutil
import subprocess

from . import Profile
from .log import error
from .paths import qutebrowser_exe


def launch_qutebrowser(
    profile: Profile | None, foreground: bool, qb_args: tuple[str, ...] = ()
) -> bool:
    qb = profile.cmdline() if profile else [qutebrowser_exe()]
    return launch(foreground, [*qb, *qb_args])


def launch(foreground: bool, args: list[str]) -> bool:
    if not shutil.which(args[0]):
        error("qutebrowser is not installed")
        return False

    if foreground:
        return subprocess.run(args, check=False).returncode == 0
    else:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            # give qb a chance to validate input before returning to shell
            stdout, stderr = p.communicate(timeout=0.1)
            print(stderr.decode(errors="ignore"), end="")
        except subprocess.TimeoutExpired:
            pass

    return True
