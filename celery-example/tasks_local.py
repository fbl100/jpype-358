import sys
import os
import jpype

from celery import Celery

app = Celery('tasks', broker='amqp://localhost')

# define a task to perform busy work by calculating a portion of the mandelbrot fractal
# on a 2017 Macbook Pro this takes ~5 seconds
@app.task
def mandelbrot():

    # if the JVM is not started, start it
    if not jpype.isJVMStarted():
        print("starting jvm")
        classpath = "../mandelbrot-calc/build/libs/mandelbrot-calc-0.0.2-all.jar"
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % classpath)
        print("jvm has started")

    # create the JClass for the Mandelbrot
    Mandelbrot = jpype.JClass("com.example.calculation.Mandelbrot")

    # run it
    print("starting mandelbrot calculation")
    count = Mandelbrot.doMandelBrot(-0.5, 0.0)
    print("finished in " + str(count) + " millis")










