import datetime
import pytz
from jpype import JArray, JClass

def getOptionalInstance(x):
    if type(x) is list:
        internalObjects = list(getOptionalInstance(thing) for thing in x)
        className = JClass(internalObjects[0].getClass().getName())
        retVal = JArray(className, 1)(internalObjects)
        return retVal

    if type(x) is dict:
        # local import necessary to avoid a circular dependency - import it when you need it
        from blnx.java.util.HashMap import JHashMap
        hashMap = JHashMap()
        for key,value in x.items():
            hashMap.put(key, getOptionalInstance(value))
        return hashMap



    if hasattr(x, 'instance'):
        return x.instance
    else:
        return x

def parse8601Z(timeString):

    s = timeString.replace("Z", "")
    if "." not in s:
        s = s + ".0"

    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=pytz.UTC)

