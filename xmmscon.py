import os

from xmmsclient import XMMS
from xmmsclient.glib import GLibConnector

import gobject

__all__ = ["XmmsConnection"]

CLIENT_ID = 'carpc'

def value_wrap(cb):
    if cb:
        #TODO may want to add check for value type
        try: return lambda value: cb(value.value())
        except: logging.exception("Exception in callback")
    else:
        return None

_full_conversion_dict = {
    'samplerate':(u'plugin/mad', u'samplerate'),        # audio sampling rate (44.1kHz)
    'url':(u'server', u'url'),                          # server url
    'added':(u'server', u'added'),                      # timestamp of when the track was added
    'sampleformat':(u'plugin/mad', u'sample_format'),   # sample format? ('S16')
    'tracknumber':(u'plugin/id3v2', u'tracknr'),        # the track number from the album
    'chain':(u'server', u'chain'),                      # WTF is this? ('file:magic:id3v2:magic:mad:segment')
    'channels':(u'plugin/mad', u'channels'),            # number of audio channels in the track
    'mime':(u'plugin/magic', u'mime'),                  # the track's filetype ('audio/mpeg')
    'playcount':(u'server', u'timesplayed'),            # number of times the track has been played
    'lastplayed':(u'server', u'laststarted'),           # timestamp from when the song was last started
    'filesize':(u'plugin/file', u'size'),               # size of the file
    'bitrate':(u'plugin/mad', u'bitrate'),              # the bitrate of the track
    'id':(u'server', u'id'),                            # the id of the track in the medialib
    'title':(u'plugin/id3v2', u'title'),                # the title of the track
    'artist':(u'plugin/id3v2', u'artist'),              # the track's artist
    'album':(u'plugin/id3v2', u'album'),                # the album the track is from
    'length':(u'plugin/mad', u'duration')               # the duration of the song in milliseconds
}

_basic_conversion_dict = {
    # 'samplerate':(u'plugin/mad', u'samplerate'),        # audio sampling rate (44.1kHz)
    # 'url':(u'server', u'url'),                          # server url
    # 'added':(u'server', u'added'),                      # timestamp of when the track was added
    # 'sampleformat':(u'plugin/mad', u'sample_format'),   # sample format? ('S16')
    # 'tracknumber':(u'plugin/id3v2', u'tracknr'),        # the track number from the album
    # 'chain':(u'server', u'chain'),                      # WTF is this? ('file:magic:id3v2:magic:mad:segment')
    # 'channels':(u'plugin/mad', u'channels'),            # number of audio channels in the track
    # 'mime':(u'plugin/magic', u'mime'),                  # the track's filetype ('audio/mpeg')
    # 'playcount':(u'server', u'timesplayed'),            # number of times the track has been played
    # 'lastplayed':(u'server', u'laststarted'),           # timestamp from when the song was last started
    # 'filesize':(u'plugin/file', u'size'),               # size of the file
    # 'bitrate':(u'plugin/mad', u'bitrate'),              # the bitrate of the track
    'id':(u'server', u'id'),                            # the id of the track in the medialib
    'title':(u'plugin/id3v2', u'title'),                # the title of the track
    'artist':(u'plugin/id3v2', u'artist'),              # the track's artist
    'album':(u'plugin/id3v2', u'album'),                # the album the track is from
    'length':(u'plugin/mad', u'duration')               # the duration of the song in milliseconds
}

def convert_medialib_metadata_basic(ml_data):
    data = {'length':None, 'title':None, 'artist':None, 'album':None, 'id':None}
    conversion_dict = _basic_conversion_dict
    for k, v in conversion_dict.items():
        try: data[k] = ml_data[v]
        except:
            print "metadata conversion error: key '%s' from '%s'"%(str(k), str(v))
    return data

class SeekException(Exception):
    pass

class XmmsConnection(gobject.GObject):
    
    __gsignals__ = {
        'xmmsdisconnected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
        'xmmsconnected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }
    

    def __init__(self):
        gobject.GObject.__init__(self)

        self.connected = False
        self.xmms = None
        
        self.ext_pb_status_cb = None
        self.ext_pb_current_id_cb = None
        self.ext_pb_playtime_cb = None
        
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
    
    #connection status change callbacks
    def do_xmmsconnected(self, connected):
        print "made xmms connection"
        self._select_main_playlist()
        # self.playlist_shuffle() #new
        self._register_main_callbacks()
        print "con made"
        
        
    def do_xmmsdisconnected(self, connected):
        print "lost xmms connection"

    #init functions
    def _select_main_playlist(self):
        res = self.xmms.playlist_load(playlist="MAIN")
        res.wait()
    
    def _register_main_callbacks(self):
        print "_register_main_callbacks"
        self.xmms.signal_playback_playtime(self._playback_playtime_callback)
        self.xmms.broadcast_playback_current_id(self._playback_current_id_callback)
        self.xmms.broadcast_playback_status(self._playback_status_callback)
        
    
    #callback functions
    def _playback_status_callback(self, r):
        statuses = ["Stopped", "Playing", "Paused"]
        status = statuses[r.value()]
        print "playback_status_callback - status: %s"% status
        #call external callback
        if self.ext_pb_status_cb:
            self.ext_pb_status_cb(status)
    
    def _playback_current_id_callback(self, r):
        # print "playback_current_id_callback"
        # print r.value()
        #call external callback
        if self.ext_pb_current_id_cb:
            self.ext_pb_current_id_cb(r.value())
    
    def _playback_playtime_callback(self, r):
        # print "playback_playtime_callback"
        # print r.value()
        #call external callback
        if self.ext_pb_playtime_cb:
            self.ext_pb_playtime_cb(r.value())
    

    #register external callbacks
    def register_playback_status_callback(self, cb=None):
        self.ext_pb_status_cb = cb# = value_wrap(cb)
    
    def register_playback_current_id_callback(self, cb=None):
        self.ext_pb_current_id_cb = cb#= value_wrap(cb)
    
    def register_playback_playtime_callback(self, cb=None):
        self.ext_pb_playtime_cb = cb#= value_wrap(cb)

    #volume control functions
    def set_volume(self, name, volume, cb=None):
        self.xmms.playback_volume_set(name, volume, value_wrap(cb))

    def get_volume(self, cb):
        self.xmms.playback_volume_get(value_wrap(cb))
    
    #playlist control functions
    def get_playlists(self, cb):
        self.xmms.playlist_list(value_wrap(cb))
    
    def set_playlist(self, playlist, cb=None):
        self.xmms.playlist_load(playlist=playlist, cb=value_wrap(cb))
    
    def playlist_shuffle(self):
        self.xmms.playlist_shuffle()
    
    #metadata functions
    def get_metadata(self, media_id, cb):
        if media_id is None:
            #use current song
            res = self.xmms.playback_current_id()
            res.wait()
            media_id = res.value()
        if media_id:
            self.xmms.medialib_get_info(media_id, cb=value_wrap(cb))
        else:
            cb(None)
    
    def get_metadata_blocking(self, media_id=None):
        xmms = self.xmms
        if media_id is None:
            res = xmms.playback_current_id()
            res.wait()
            media_id = res.value()
        if media_id:
            res = xmms.medialib_get_info(media_id)
            res.wait()
            return convert_medialib_metadata_basic(res.value())
        return None

    #playback control functions
    def get_status(self, cb=None):
        if cb:
            self.xmms.playback_status(value_wrap(cb))
        else:
            res = self.xmms.playback_status()
            res.wait()
            return res.value()
    
    def get_playback_playtime(self, cb=None):
        if cb:
            self.xmms.playback_playtime(value_wrap(cb))
        else:
            res = self.xmms.playback_status()
            res.wait()
            return res.value()
            
    def get_status_blocking(self):
        res = self.xmms.playback_status()
        res.wait()
        return res.value()
        
    def pause(self, cb=None):
        if cb:
            self.xmms.playback_pause(value_wrap(cb))
        else:
            res = self.xmms.playback_pause()
            res.wait()
            print "pause: ", res.value()
    
    def play(self, cb=None):
        if cb:
            self.xmms.playback_start(value_wrap(cb))
        else:
            res = self.xmms.playback_start()
            res.wait()
            print "play: ", res.value()
        # self.xmms.playback_start(value_wrap(cb))

    def stop(self, cb=None):
        if cb:
            self.xmms.playback_stop(value_wrap(cb))
        else:
            res = self.xmms.playback_stop()
            res.wait()
            print "stop: ", res.value()
        # self.xmms.playback_stop(value_wrap(cb))
    
    def seek(self, time_ms, cb=None):
        #seek only works if playing....
        
        xmms = self.xmms
        
        #get current status
        ps_res = xmms.playback_status()
        ps_res.wait()
        status = ps_res.value()
        if status != 1:
            #need to set to playing to seek
            raise SeekException("must be playing to seek")
        else:
            if cb:
                is_ready = True
            else:
                is_ready = False
            def seek_cb(r):
                print "seek_cb is_error: ", r.is_error()
                print "seek_cb value: ", r.value()
                if cb:
                    cb(r.value())
                else:
                    is_ready = True
            
            xmms.playback_seek_ms(time_ms, cb=seek_cb)
            while not is_ready:
                pass
            return
            # if cb:
            #     self.xmms.playback_seek_ms(time_ms, cb=value_wrap(cb))
            # else:
            #     res = self.xmms.playback_seek_ms(time_ms)
            #     res.wait()
            #     print "seek: ", res.value()
            
        
        # def seek_cb(r):
        #     if cb:
        #         cb(r.value())
        # self.xmms.playback_seek_ms(time_ms, cb=value_wrap(cb))
        # if cb:
        #     self.xmms.playback_seek_ms(time_ms, cb=value_wrap(cb))
        # else:
        #     res = self.xmms.playback_seek_ms(time_ms)
        #     res.wait()
        #     print "seek: ", res.value()
        # self.xmms.playback_seek_ms(time_ms, cb=value_wrap(cb))
    
    #TODO improve shuffling system....
    def next(self, cb=None):
        self._go_rel(1, cb=value_wrap(cb))

    def prev(self, cb=None):
        self._go_rel(-1, cb=value_wrap(cb))

    def _go_rel(self, delta, cb=None):
        xmms = self.xmms

        # def status_cb(status):
        #     if status != self.STATUS_PLAY:
        #         self.start(cb)
        #     elif cb:
        #         cb(status)

        def tickle_cb(value):
            print "tickle_cb ", value
            if cb:
                cb(value)
            # self.get_status(status_cb)

        def next_cb(value):
            xmms.playback_tickle(tickle_cb)

        xmms.playlist_set_next_rel(delta, cb=next_cb)
gobject.type_register(XmmsConnection)
