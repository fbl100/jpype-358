# JPYPE DEADLOCK ENVIRONMENT
This repository is intended to help reproduce the situation discussed in 
Issue #358 of the Jpype project.  

https://github.com/jpype-project/jpype/issues/358

# Introduction
To reproduce the problem, I have created a very simple celery task that
calls a java function to simulate a long running task by calculating a 
section of the mandelbrot fractal.  On a 2018 Macbook pro, this takes
~5 seconds to complete.

There are two separate celery task files included.

```tasks_local.py``` starts the JVM on a worker thread when the task is activated
```tasks_global.py``` starts the JVM outside of the worker thread on application startup

## tasks_local bug
Even though the worker contains a guard to prevent multiple JVM's from starting, the 
logs appear to show one per thread...

## tasks_global bug
When the JVM is started at the top of the file, the call to mandelbrot() appears to
deadlock and never return

## Environment

### Python VirtualEnv
To create the virtual environment, use the following commands
```bash
cd celery-example
virtualenv venv
source venv/bin/activate
pip install celery
pip install numpy
pip install JPype1 (or you can build it from source)
``` 
or (on Amazon AMI)
```bash
cd celery-example
python3 -m venv venv
source venv/bin/activate
pip install celery
pip install numpy
pip install JPype1 (or you can build it from source)
``` 

### Java
This has been reproduced with Oracle jdk8 update 172 and OpenJDK 10 on a OSX High Sierra (10.13.6) 

The library included is already compiled.  In the event that you want to mess with the java
side, I have included the source for the mandelbrot calculation in the mandelbrot-calc directory.
To build it, issue the following commands:
```
cd mandelbrot-calc
./gradlew :shadowJar
```

### RabbitMQ (Terminal 1)
The easiest way to start RabbitMQ is to use the following docker command

```docker run -p 5672:5672 -p 15672:15672 rabbitmq:3.6-management```

# Reproducing the Deadlock

## (Terminal 2) Start Celery
```
cd celery-example
source ./venv/bin/activate
celery -A tasks_global worker --loglevel=info

Expected Output:
starting jvm
jvm has started
 
 -------------- celery@macbook-pro-3.lan v4.2.1 (windowlicker)
---- **** ----- 
--- * ***  * -- Darwin-17.7.0-x86_64-i386-64bit 2018-11-07 15:09:02
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x101ec9b38
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . tasks_global.mandelbrot

[2018-11-07 15:09:03,221: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2018-11-07 15:09:03,238: INFO/MainProcess] mingle: searching for neighbors
[2018-11-07 15:09:04,288: INFO/MainProcess] mingle: all alone
[2018-11-07 15:09:04,317: INFO/MainProcess] celery@macbook-pro-3.lan ready.
```

## (Terminal 3) Send a task
```
cd celery-example
source ./venv/bin/activate
python

Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 26 2018, 19:50:54) 
[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license" for more information.

>>> from tasks_global import *

starting jvm
jvm has started

# this runs the java code in this python terminal, not via celery
# it is simply here to prove that the mandelbrot calculation does in-fact finish
>>> mandelbrot()

starting mandelbrot calculation
finished in 5346 millis

# this sends the request to the celery instance we started in Terminal 2
>>> mandelbrot.delay()
<AsyncResult: 2c52d780-9107-4fd9-bbb9-c16e71b0c838>
```

## (Terminal 2) Expected Output
```bash
[2018-11-07 15:09:03,221: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2018-11-07 15:09:03,238: INFO/MainProcess] mingle: searching for neighbors
[2018-11-07 15:09:04,288: INFO/MainProcess] mingle: all alone
[2018-11-07 15:09:04,317: INFO/MainProcess] celery@macbook-pro-3.lan ready.
[2018-11-07 15:14:08,643: INFO/MainProcess] Received task: tasks_global.mandelbrot[2c52d780-9107-4fd9-bbb9-c16e71b0c838]  
[2018-11-07 15:14:08,648: WARNING/ForkPoolWorker-7] starting mandelbrot calculation
```

At this point, the celery window fails to respond or return from the calculation




# Reproducing the Multi-JVM

## (Terminal 2) Start Celery
```
cd celery-example
celery -A tasks_local worker --loglevel=info

15:25 $ celery -A tasks_local worker --loglevel=info
 
 -------------- celery@macbook-pro-3.lan v4.2.1 (windowlicker)
---- **** ----- 
--- * ***  * -- Darwin-17.7.0-x86_64-i386-64bit 2018-11-07 15:25:31
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x1074b1a90
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . tasks_local.mandelbrot

[2018-11-07 15:25:31,955: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2018-11-07 15:25:31,973: INFO/MainProcess] mingle: searching for neighbors
[2018-11-07 15:25:33,013: INFO/MainProcess] mingle: all alone
[2018-11-07 15:25:33,034: INFO/MainProcess] celery@macbook-pro-3.lan ready.

```

## (Terminal 3) Send Multiple Tasks
```
cd celery-example
python

Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 26 2018, 19:50:54) 
[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from tasks_local import *
>>> mandelbrot.delay()
<AsyncResult: c2c91689-d0ba-4579-82d8-c9eb5367dd52>
>>> mandelbrot.delay()
<AsyncResult: 792c5daa-60f2-4569-ba95-f54ec274c7e0>
>>> mandelbrot.delay()
<AsyncResult: a745345e-3d44-4c6b-a38a-8e682fadac67>
>>> mandelbrot.delay()
<AsyncResult: a25aa85e-c872-48cb-9992-efd7d07f28f7>
>>> mandelbrot.delay()
<AsyncResult: 6907dc6a-99f3-4468-996d-529e3101ce22>
>>> mandelbrot.delay()
<AsyncResult: 711546b3-c915-44ba-9167-3f17b1acc9a9>
>>> mandelbrot.delay()
<AsyncResult: e2d47f0b-9f64-4333-b6a1-66e555769e68>
>>> mandelbrot.delay()
<AsyncResult: 7cb260d0-90b2-4c5f-8077-102bf39aea6b>
```

## (Terminal 2) Expected Output
```bash
[2018-11-07 15:25:33,034: INFO/MainProcess] celery@macbook-pro-3.lan ready.
[2018-11-07 15:26:50,424: INFO/MainProcess] Received task: tasks_local.mandelbrot[c2c91689-d0ba-4579-82d8-c9eb5367dd52]  
[2018-11-07 15:26:50,427: WARNING/ForkPoolWorker-8] starting jvm
[2018-11-07 15:26:50,548: WARNING/ForkPoolWorker-8] jvm has started
[2018-11-07 15:26:50,572: WARNING/ForkPoolWorker-8] starting mandelbrot calculation
[2018-11-07 15:26:55,641: WARNING/ForkPoolWorker-8] finished in 5063 millis
[2018-11-07 15:26:55,642: INFO/ForkPoolWorker-8] Task tasks_local.mandelbrot[c2c91689-d0ba-4579-82d8-c9eb5367dd52] succeeded in 5.215689828997711s: None
[2018-11-07 15:26:57,068: INFO/MainProcess] Received task: tasks_local.mandelbrot[792c5daa-60f2-4569-ba95-f54ec274c7e0]  
[2018-11-07 15:26:57,071: WARNING/ForkPoolWorker-2] starting jvm
[2018-11-07 15:26:57,180: WARNING/ForkPoolWorker-2] jvm has started
[2018-11-07 15:26:57,204: WARNING/ForkPoolWorker-2] starting mandelbrot calculation
[2018-11-07 15:26:59,971: INFO/MainProcess] Received task: tasks_local.mandelbrot[a745345e-3d44-4c6b-a38a-8e682fadac67]  
[2018-11-07 15:26:59,973: WARNING/ForkPoolWorker-4] starting jvm
[2018-11-07 15:27:00,076: WARNING/ForkPoolWorker-4] jvm has started
[2018-11-07 15:27:00,099: WARNING/ForkPoolWorker-4] starting mandelbrot calculation
[2018-11-07 15:27:02,745: WARNING/ForkPoolWorker-2] finished in 5531 millis
[2018-11-07 15:27:02,746: INFO/ForkPoolWorker-2] Task tasks_local.mandelbrot[792c5daa-60f2-4569-ba95-f54ec274c7e0] succeeded in 5.675980783998966s: None
[2018-11-07 15:27:05,674: WARNING/ForkPoolWorker-4] finished in 5567 millis
[2018-11-07 15:27:05,675: INFO/ForkPoolWorker-4] Task tasks_local.mandelbrot[a745345e-3d44-4c6b-a38a-8e682fadac67] succeeded in 5.702280108991545s: None
[2018-11-07 15:27:07,562: INFO/MainProcess] Received task: tasks_local.mandelbrot[a25aa85e-c872-48cb-9992-efd7d07f28f7]  
[2018-11-07 15:27:07,569: WARNING/ForkPoolWorker-6] starting jvm
[2018-11-07 15:27:07,680: WARNING/ForkPoolWorker-6] jvm has started
[2018-11-07 15:27:07,704: WARNING/ForkPoolWorker-6] starting mandelbrot calculation
[2018-11-07 15:27:09,939: INFO/MainProcess] Received task: tasks_local.mandelbrot[6907dc6a-99f3-4468-996d-529e3101ce22]  
[2018-11-07 15:27:09,942: WARNING/ForkPoolWorker-8] starting mandelbrot calculation
[2018-11-07 15:27:11,163: INFO/MainProcess] Received task: tasks_local.mandelbrot[711546b3-c915-44ba-9167-3f17b1acc9a9]  
[2018-11-07 15:27:11,164: WARNING/ForkPoolWorker-2] starting mandelbrot calculation
[2018-11-07 15:27:12,379: INFO/MainProcess] Received task: tasks_local.mandelbrot[e2d47f0b-9f64-4333-b6a1-66e555769e68]  
[2018-11-07 15:27:12,381: WARNING/ForkPoolWorker-4] starting mandelbrot calculation
[2018-11-07 15:27:13,958: WARNING/ForkPoolWorker-6] finished in 6245 millis
[2018-11-07 15:27:13,960: INFO/ForkPoolWorker-6] Task tasks_local.mandelbrot[a25aa85e-c872-48cb-9992-efd7d07f28f7] succeeded in 6.392899204001878s: None
[2018-11-07 15:27:15,799: WARNING/ForkPoolWorker-8] finished in 5855 millis
[2018-11-07 15:27:15,800: INFO/ForkPoolWorker-8] Task tasks_local.mandelbrot[6907dc6a-99f3-4468-996d-529e3101ce22] succeeded in 5.858714564994443s: None
[2018-11-07 15:27:16,569: WARNING/ForkPoolWorker-2] finished in 5405 millis
[2018-11-07 15:27:16,570: INFO/ForkPoolWorker-2] Task tasks_local.mandelbrot[711546b3-c915-44ba-9167-3f17b1acc9a9] succeeded in 5.406114019991946s: None
[2018-11-07 15:27:17,679: WARNING/ForkPoolWorker-4] finished in 5298 millis
[2018-11-07 15:27:17,680: INFO/ForkPoolWorker-4] Task tasks_local.mandelbrot[e2d47f0b-9f64-4333-b6a1-66e555769e68] succeeded in 5.29932462600118s: None
[2018-11-07 15:27:22,661: INFO/MainProcess] Received task: tasks_local.mandelbrot[7cb260d0-90b2-4c5f-8077-102bf39aea6b]  
[2018-11-07 15:27:22,662: WARNING/ForkPoolWorker-6] starting mandelbrot calculation
[2018-11-07 15:27:27,480: WARNING/ForkPoolWorker-6] finished in 4817 millis
[2018-11-07 15:27:27,481: INFO/ForkPoolWorker-6] Task tasks_local.mandelbrot[7cb260d0-90b2-4c5f-8077-102bf39aea6b] succeeded in 4.81866276000801s: None
```

the JVM is started once per thread

