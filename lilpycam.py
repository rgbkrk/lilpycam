#!/usr/bin/env python

'''
This is just a simple little extension of BaseHTTPRequestHandler that grabs
images from a webcam and hosts them as PNGs.

Simple run::

  $ python lilpycam.py 127.0.0.1 8000
  Running server on http://127.0.0.1:8000

'''

import sys,os
import cv
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Initialization of the camera
camera_index = 0
capture = cv.CaptureFromCAM(camera_index)

# Keep track of clients
clientsSoFar = set()

# HTML code we'll be spitting for the primary view of the camera
refreshHTML = '''
<html>
<head>
<title>SANDYCAM</title>
<style type="text/css">
    .centered {
      position: fixed;
      top: 50%;
      left: 50%;
      margin-left: ''' + str(-160) +'''px;
      margin-top: ''' + str(-120) + '''px;
    }
    body {
        background-color: #606060;
    }
</style>
<script src="http://code.jquery.com/jquery-latest.js"></script>
<script>
 $(document).ready(function() {
   $('#cam').bind('load', function() {
        // You loaded one, why not get another?
        d = new Date();
        $("#cam").attr("src", "/cam.png?t="+d.getTime());
   });
   $.ajaxSetup({ cache: false });
});
</script>
</head>
<body>
<img id="cam" class="centered" src="cam.png">
</body>

'''

class WebCamHTTPRequestHandler(BaseHTTPRequestHandler):
    '''
    Just a simple handler that only serves two files

    * PNGs from the webcam (/*.png*)
    * A simple html page that refreshes for the user (all other paths)

    '''

    def do_GET(self):
        '''
        Overrides the base do_GET to simply track new clients,
        create PNGs from the webcam, and host a simple web page to
        display the camera view
        '''
        try:
            cli = self.client_address[0]
            if cli not in clientsSoFar:
                clientsSoFar.add(cli)
                print "New Client %s" % cli
                print "Clients overall:"
                print clientsSoFar

            if '.png' in self.path:
                # Create a PNG from the webcam
                im = cv.QueryFrame(capture)
                png = cv.EncodeImage(".png",im)

                #send code 200 response
                self.send_response(200)
                #send header first
                self.send_header('Content-type','image/png')
                self.send_header('Connection','close')
                self.end_headers()

                # Send them the image
                self.wfile.write(png.tostring())
                self.finish()
                return
            else:
                # Otherwise, just give them the html page
                self.send_response(200)
                self.send_header('Content-type','text/html; charset=utf-8')
                self.end_headers()

                self.wfile.write(refreshHTML)
                self.finish()
                return

        except IOError:
            self.send_error(404, ':(')

def run(server,port):
    httpd = HTTPServer((server,port), WebCamHTTPRequestHandler)
    print "Running server on http://%s:%s" % (server,port)
    httpd.serve_forever()

if __name__ == '__main__':
    server,port = '127.0.0.1',8080
    if(len(sys.argv) >= 3):
        server,port = sys.argv[1],int(sys.argv[2])
    run(server,port)

