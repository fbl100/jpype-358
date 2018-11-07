from jpype import startJVM, getDefaultJVMPath
import os
import sys

class JVM:
    class __JVM:
        def __init__(self):
            classpath = "./lib/blacklynx-aerospace.jar"
            if os.environ.get('BLNX_JAVA_CLASSPATH') is not None:
                print("using environment variable BLNX_JAVA_CLASSPATH for classpath", file=sys.stderr)
                classpath = os.environ.get('BLNX_JAVA_CLASSPATH')
            else:
                print("using default classpath of " + classpath, file=sys.stderr)
                print("set environment variable BLNX_JAVA_CLASSPATH to specify a location necessary", file=sys.stderr)

            print("JVM path  : " + getDefaultJVMPath(), file=sys.stderr)
            print("classpath : " + classpath, file=sys.stderr)
            startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % classpath)
            print("JVM started...", file=sys.stderr)
            self.__JVM_STARTED__ = True

        def __str__(self):
            return "JVM Instance"

    instance = __JVM()
