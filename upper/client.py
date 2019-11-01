from queue import Queue
from concurrent import futures
import time
import random
import functools
import threading

import grpc
from .HelloWorld_pb2_grpc import GreeterStub
from .HelloWorld_pb2 import HelloRequest


def continuous_sender(itr, context):
    global _last_index
    try:
        print("New connection to server...")
        chan = grpc.insecure_channel("127.0.0.1:7000")
        fut = grpc.channel_ready_future(chan)

        while not fut.done():
            print("channel is not ready")
            time.sleep(1)

        stub = GreeterStub(chan)

        if context[0] != context[1][0]:
            for result in stub.SayHello((x[1] for x in [context[1]])):
                print("BACKLOG Result:", result.id, result.message)
                context[0] = result.id
            
        for result in stub.SayHello(itr):
            print("Result:", result.id, result.message)
            context[0] = result.id
    except Exception as exc:
        print(exc)
    chan.close()
    print("Exiting continuous_sender...")

def request_iterator(queue, context):
    datum = queue.get()
    context[1] =  datum
    print("Extracted:", datum[0], threading.get_ident())
    return(datum[1])


def message_generator(queue):
    count = 0
    while True:
        time.sleep(1)
        datum = HelloRequest(id=count, name="".join(random.choices("abcdefghikjlmnopqrstuvwxyz", k=16)))
        print(f"Generating {count}:", datum)
        queue.put((count, datum))
        count += 1


if __name__ == "__main__":
    queue = Queue()
    worker = threading.Thread(target=message_generator, args=(queue,))
    worker.start()

    print("Main thread", threading.get_ident())
    context = {0: -1, 1: (-1, None)}
    while True:
        continuous_sender(
            iter(functools.partial(request_iterator, queue, context), None),
            context
        )
        time.sleep(10)
    
