import jpype


from celery import Celery

app = Celery('tasks', broker='amqp://localhost')

# start the JVM right away
if not jpype.isJVMStarted():
    print("starting jvm")
    classpath = "../mandelbrot-calc/build/libs/mandelbrot-calc-0.0.2-all.jar"
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % classpath)
    print("jvm has started")

# create the JClass right away
Mandelbrot = jpype.JClass("com.example.calculation.Mandelbrot")

@app.task
def mandelbrot():

    # attach to the JVM if necessary
    if not jpype.isThreadAttachedToJVM():
        print("attaching to JVM")
        jpype.attachThreadToJVM()

    # start the calculation (this will never complete)
    print("starting mandelbrot calculation")
    count = Mandelbrot.doMandelBrot(-0.5, 0.0)
    print("finished in " + str(count) + " millis")










