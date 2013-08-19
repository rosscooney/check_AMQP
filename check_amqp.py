#!/usr/bin/python2.6

'''
Software License Agreement (BSD License)

Copyright (c) 2013, Smith Electric Vehicles (Europe) Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

  Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

  Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Dependencies:
py-amqplib : http://code.google.com/p/py-amqplib/
'''

from amqplib import client_0_8 as amqp
import sys
import random
import time

''' Connection details go here '''
amqpServer = "host:port"
amqpQueue = "queuename"
amqpVhost = "/"
amqpSsl = True
amqpUid = "username"
amqpPass = "password"

''' Number of seconds before message is considered timed out'''
timeout = 4
''' Number of seconds before the received message is considered late and a warning is raised'''
recievedTimeWarning = 2

''' Function to check the header of a passed message and check it. If it matches the sent message
the function checks the time it took to arrive and exits with the appropriate state. If the message does not
match the sent message ID it is discarded. '''
def recieve_callback(msg):
    recTime = time.time()
    recMessageID = msg.application_headers['messID']
    timeDiff = recTime - sendTime

    if recMessageID == messageID and timeDiff < recievedTimeWarning:
        print "Test message received in %s seconds" % timeDiff
        sys.exit(0)
        amqpChan.close()
        amqpConn.close()
    if recMessageID == messageID and timeDiff > recievedTimeWarning:
        print "Test message received in %s seconds" % timeDiff
        amqpChan.close()
        amqpConn.close()
        sys.exit(1)
    pull_message()

''' Funtion to pull a single message from the queue and continue checking for messages until the timeout is reached  '''
def pull_message():
    slept = 0
    sleepInterval = 0.1
    while slept < timeout:
        msg = amqpChan.basic_get(amqpQueue)
        if msg is not None:
            amqpChan.basic_ack(msg.delivery_tag)
            recieve_callback(msg)
        time.sleep(sleepInterval)
        slept += sleepInterval
    print "Timeout (%s seconds) expired while waiting for test message." % timeout
    amqpChan.close()
    amqpConn.close()
    sys.exit(2)

''' A try to test connection to the AMQP resource. If the connection fails the script exits with a critical exit status '''
try:
    amqpConn = amqp.Connection(host=amqpServer, userid=amqpUid, password=amqpPass, virtual_host=amqpVhost, insist=False, ssl=amqpSsl)
    amqpChan = amqpConn.channel()
    amqpChan.queue_declare(queue=amqpQueue, durable=True, auto_delete=False)
    amqpChan.exchange_declare(exchange=amqpQueue, type="direct", durable=True, auto_delete=False,)
    amqpChan.queue_bind(queue=amqpQueue, exchange=amqpQueue, routing_key=amqpQueue)
except:
    print "Cannot connect to queue: %s on %s" % (amqpQueue, amqpServer)
    amqpChan.close()
    amqpConn.close()
    sys.exit(2)

''' Generating a random message ID and sending a single message '''
messageID = str(random.randint(1,1000000))
testMsg = amqp.Message(messageID,application_headers={'messID': messageID})
testMsg.properties["delivery_mode"] = 1
sendTime = time.time()
amqpChan.basic_publish(testMsg,exchange=amqpQueue,routing_key=amqpQueue)

pull_message()
