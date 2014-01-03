Introduction
==============

check_AMQP is a small Nagios plugin that tests an AMQP resource by sending a message, collecting it and calculating the round trip time.

The purpose of this plugin is test the full stack availability of your AMQP resource by checking the ability to connect and the speed of message return. So far the script has been tested with Nagios 3.3 on Ubuntu 10.04 and with the folloing AMQP services:
  * StormMQ AMQP service (www.stormmq.com).
  * RabbitMQ 2.8.7xxx

This script only supports AMQP 0.8 and should work with all AMQP 0.8 compatible services, however we have not tested this.

Usage
==========

The script allows you to specify your connection details to your resource and then it tries to connect to your specified queue. If the connection fails the plugin returns a critical exit code.

I recommend you use a queue that is solely for this plugin, as it will drop any messages that it’s not expecting.

Once connected the plugin publishes a single message to the queue with a random message ID and then waits until the message is received. If your specified timeout is reached before the message is received the plugin will return a critical exit code.

If the message is received the plugin checks if it is above or below the recievedTimeWarning threshold and either exits OK or with a warning.

Install Instructions
==========

Assuming that Nagios is installed in the default directory (/usr/local/nagios/libexec/).

Place the file in this directory:
/usr/local/nagios/libexec/

Installation with virtualenv
----------------------------

    cd /usr/local/nagios/libexec/
    git clone <repourl>
    cd check_AMQP
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

Configuration
=============
An example of the text you can add to the nagios config file:

    define host{
            use                     linux-server
            host_name               AMQPserver
            alias                   AMQPserver
            address                 <<IP ADDRESS OF SERVER>>
    }
    
    define command {
            command_name    check_amqp
            command_line    /usr/lib/nagios/plugins/check_AMQP/check_amqp --ssl --host '$HOSTADDRESS$' --port 5672 --queue monitoring_test_queue --vhost '$ARG1$' --user '$ARG2$' --password '$ARG3$' --warning 0.05 --critical 0.5
    }
    
    define service{
            use                             generic-service
            host_name                       AMQPserver
            service_description             Check AMQP Connection
            check_command                   check_amqp!/!guest!guest
    }

Requirements
==============
  * Python 2.6
  * py-amqplib : http://code.google.com/p/py-amqplib/

Future
==============
* Testing on other AMQP services
* Support for AMQP 0.9, 0.10 and 1.0
