#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import datetime
import signal


def run(cmd, timeout=20):
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    result = process.stdout.read()
    print result
    return result


def command(cmd, timeout=10):
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        line = process.stderr.readline()
        line = line.strip()
        if line:
            print('Subprogram output: [{}]'.format(line))
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None, None
    stdoutput, erroroutput = process.communicate()
    print erroroutput
    return stdoutput, erroroutput

def subproces(cmd):
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = rst.stdout.readlines()
    print out




