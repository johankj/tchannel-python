# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import

import pytest
import socket

from tchannel.errors import AlreadyListeningError
from tchannel.tornado import TChannel


@pytest.fixture
def tchannel():
    return TChannel(name='test')


@pytest.mark.gen_test
def test_peer_caching(tchannel):
    "Connections are long-lived and should not be recreated."""
    peer = tchannel.peers.get("localhost:4040")
    assert tchannel.peers.get("localhost:4040") is peer


def test_known_peers():
    peers = ["localhost:%d" % port for port in range(4040, 4101)]
    tchannel = TChannel('test', known_peers=peers)

    for peer in peers:
        assert tchannel.peers.lookup(peer)


def test_is_listening_should_return_false_when_listen_not_called(tchannel):

    assert tchannel.is_listening() is False


def test_is_listening_should_return_true_when_listen_called(tchannel):

    tchannel.listen()

    assert tchannel.is_listening() is True


def test_should_error_if_call_listen_twice(tchannel):

    tchannel.listen()

    with pytest.raises(AlreadyListeningError):
        tchannel.listen()


def test_close_stops_listening():
    server = TChannel(name='server')
    server.listen()

    host = server.host
    port = server.port

    # Can connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.close()

    server.close()

    # Can't connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with pytest.raises(socket.error):
        sock.connect((host, port))
