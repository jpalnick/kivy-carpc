import os

from xmmsclient import XMMS
from xmmsclient.glib import GLibConnector

import gobject

CLIENT_ID = 'autoupdatexmmslist'

class AutoUpdateXmmsPlaylist(gobject.GObject):
    
    __gsignals__ = {
        'xmmsdisconnected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
        'xmmsconnected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }
    
    def __init__(self):
        gobject.GObject.__init__(self)

        self.connected = False
        self.xmms = None
        
    def connect_to_xmms(self):
        if not self.connected:
            
            #def the function that is called when disconnected from xmms
            def disconnected(r):
                self.connected = False
                self.xmms = None
                self.emit('xmmsdisconnected', self.connected)
            
            #try to connect
            try:
                xmms = self.xmms = XMMS(CLIENT_ID)
                path = os.environ.get("XMMS_PATH", None)
                xmms.connect(path, disconnect_func=disconnected)
                GLibConnector(xmms)
            except:
                self.xmms = None
                self.connected = False
            else:
                self.connected = True
                self.emit('xmmsconnected', self.connected)

        return self.connected
    
    #callback functions
    
    def medialib_entry_added_callback(self, r):
        new_id = r.value()
        self.xmms.playlist_add_id(new_id, playlist="MAIN")
        
    def do_xmmsconnected(self, connected):
        print "made xmms connection"
        self.check_playlist_exists()
        self.xmms.broadcast_medialib_entry_added(self.medialib_entry_added_callback)
        
    def do_xmmsdisconnected(self, connected):
        print "lost xmms connection"
    
    def check_playlist_exists(self):
        res = self.xmms.playlist_list()
        res.wait()
        existing_list = map(str, res.value())
        if not "MAIN" in existing_list:
            #create the main playlist
            cp_res = self.xmms.playlist_create("MAIN")
            cp_res.wait()

gobject.type_register(AutoUpdateXmmsPlaylist)

xc = None
loop = None
running = False
    
def disconnected_cb(obj, con, data=None):
    print "disconnected"
    if running:
        loop.quit()

def attempt_connect():
    print "trying to connect"
    if xc.connect_to_xmms():
        global running
        running = True
        return False
    return True
    
    
    
if __name__ == '__main__':
    xc = AutoUpdateXmmsPlaylist()
    xc.connect('xmmsdisconnected', disconnected_cb)
    
    loop = gobject.MainLoop()

    gobject.timeout_add(20, attempt_connect)
    
    loop.run()
        
