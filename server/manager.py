import json
import time
import BaseHTTPServer


config = None



class EventHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def is_Auth(self):
        """
            Simple authentication agains DOORS config.
        """
        api_key = None

        try:
            api_key = config['DOORS'][self.headers.getheader('X-Door-Id', None)]['API_KEY']
        except KeyError:
            pass

        if api_key == self.headers.getheader('X-Api-Key', None):
            return True
        else:
            return False

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def do_GET(self):
        """
            Respond to a GET request.
        """
        if self.headers.getheader('X-Door-Id', None) is None:
            self.send_error(400, "Bad Request")
        else:
            if not self.is_Auth():
                self.send_error(403, "Forbidden")
            else:
                """ 
                    Lets start the party...
                    1. Announce ring
                    2. Wait with timeout for open command
                    3. Send Command w/ DoorPw OR OK
                """
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write("OK")

    def log_message(self, format, *args):
        print "[%s]" % self.date_time_string(), \
              "- %s - %s%s" % (args[1], self.headers.getheader('X-Door-Id', 'unknown'), self.path)
        return


def load(filename):
    """
        Loads a JSON file and returns a config.
    """
    with open(filename, 'r') as settings_file:
        _config = json.load(settings_file)
    return _config


def main():
    """
        Does the basic setup and handles a ring.
    """
    global config
    config = load('manager.json')

    server_class = BaseHTTPServer.HTTPServer

    httpd = server_class((config['MANAGER_HOST'], int(config['MANAGER_PORT'])), EventHandler)
    print "[%s]" % date_time_string(), "- Server Starts - %s:%s" % (config['MANAGER_HOST'], config['MANAGER_PORT'])

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print "[%s]" % date_time_string(), "- Server Stops - %s:%s" % (config['MANAGER_HOST'], config['MANAGER_PORT'])


def date_time_string():
    """Return the current time formatted for logging."""
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        weekdayname[wd],
        day, monthname[month], year,
        hh, mm, ss)
    return s


if __name__ == "__main__":
    main()
