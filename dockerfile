FROM ubuntu 

MAINTAINER shriharsha sshripa@ncsu.edu

RUN apt-get update
RUN apt-get -y --force-yes install iproute2
RUN apt-get -y --force-yes install telnet
RUN apt-get -y --force-yes install openssh-server
RUN apt-get -y --force-yes install iptables
RUN apt-get -y --force-yes install iputils-ping
RUN apt-get -y --force-yes install traceroute
RUN apt-get -y --force-yes install tcpdump
RUN apt-get -y --force-yes install iperf
RUN apt-get -y --force-yes install vim
RUN apt-get -y --force-yes install python
RUN apt-get -y --force-yes install python-pip
RUN pip install --upgrade pip
RUN apt-get -y --force-yes install python-pexpect
RUN pip install paramiko
RUN apt-get -y --force-yes install nano
RUN apt-get -y --force-yes install keepalived
RUN apt-get -y --force-yes install conntrackd
RUN apt-get -y --force-yes install ulogd2
RUN apt-get -y --force-yes install curl

RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
RUN ln -s /usr/bin/tcpdump /usr/sbin/tcpdump

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config



