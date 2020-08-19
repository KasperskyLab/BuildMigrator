import os
import subprocess


# Python 2 CalledProcessError doesn't provide stderr
class CalledProcessError(Exception):
    def __init__(self, retcode, cmd, stdout=None, stderr=None):
        self.retcode = retcode
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "Command %r returned non-zero exit status %r" % (self.cmd, self.retcode)


# subprocess library is pretty good in Python 3.7
# but many things are not available in Python 2:
# * Popen.__exit__
# * CalledProcessError.stderr
# * subprocess.run() method
# * capture_output kwarg
# This function is intended to hide Python 2 deficiencies,
# while providing some of Python 3 convenience that we need.
def check_output(args, **kwargs):
    assert kwargs.get("stdout") is None
    assert kwargs.get("stderr") is None
    kwargs["stdout"] = subprocess.PIPE
    kwargs["stderr"] = subprocess.PIPE
    cwd = kwargs.get("cwd")
    if cwd and not os.path.exists(cwd):
        raise ValueError("Directory does not exist: %r" % cwd)
    process = subprocess.Popen(args, **kwargs)
    try:
        stdout, stderr = process.communicate()
    except Exception:  # Including KeyboardInterrupt
        process.kill()
        process.wait()
        raise
    if type(stdout) is not str:
        stdout = stdout.decode("ascii", "replace")
    if type(stderr) is not str:
        stderr = stderr.decode("ascii", "replace")
    retcode = process.poll()
    if retcode:
        raise CalledProcessError(retcode, args, stdout=stdout, stderr=stderr)
    return stdout, stderr
