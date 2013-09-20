import kivy
#kivy.require('1.7.1')

# from kivy.interactive import InteractiveLauncher

#main app base
from kivy.app import App

#gui layout classes
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

#GUI object classes
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
# from kivy.uix.listview import ListView
# from kivy.uix.listview import ListItemButton, ListItemLabel, CompositeListItem, ListView

# from kivy.adapters.dictadapter import DictAdapter
from kivy.properties import ObjectProperty, NumericProperty#, StringProperty, DictProperty, 
from kivy.config import Config
# from kivy.event import EventDispatcher

from kivy.clock import Clock

from kivy.support import install_gobject_iteration
install_gobject_iteration()

from math import floor
from types import *
from xmmscon import XmmsConnection, SeekException

import gobject
from platform import system as platform_system

# def gen_cb(value):
#     print "gen_cb: ", value
# 

from kivy.uix.widget import Widget

if platform_system() == "Darwin":
    #running on mac so use mac control...
    from osax import *
    def _set_sys_volume():
        


class VolumeWidget(Widget):
    def __init__(self, **kwargs):
        super(VolumeWidget, self).__init__(**kwargs)
        
    
        

class MediaBar2(Widget):
    
    def __init__(self, xmmscon, **kwargs):
        super(MediaBar2, self).__init__(**kwargs)
        self.xmms = xmmscon
        self.is_seeking = False
        # self._setup_contents()
        # self._trigger_layout = Clock.create_trigger(self.do_layout, -1)
        # self.bind(
        #     spacing=self._trigger_layout,
        #     padding=self._trigger_layout,
        #     children=self._trigger_layout,
        #     orientation=self._trigger_layout,
        #     parent=self._trigger_layout,
        #     size=self._trigger_layout,
        #     pos=self._trigger_layout)

    # def __init__(self, **kwargs):
    #     if self.__class__ == Layout:
    #         raise Exception('The Layout class cannot be used.')
    #     self._trigger_layout = Clock.create_trigger(self.do_layout, -1)
    #     super(Layout, self).__init__(**kwargs)
    def setup_contents(self):
        x = self.x
        center_y = self.center_y
        top = self.top
        
        # data_width = 600
        # data_x = 10
        # data_text_height = 15
        
        #create objects
        title_label = Label(text="Waiting", size_hint=(None, None))
        artist_label = Label(text="Waiting", size_hint=(None, None))
        album_label = Label(text="Waiting", size_hint=(None, None))
        playtime_label = Label(text="00:00", size_hint=(None, None))
        length_label = Label(text="00:00", size_hint=(None, None))
        playback_slider = Slider(min=0, max=0, value=0, size_hint=(None, None))
        next_btn = Button(text="Waiting", size_hint=(None, None))
        prev_btn = Button(text="Waiting", size_hint=(None, None))
        play_btn = Button(text="Waiting", size_hint=(None, None))
        # vol_up_btn = Button(text="Waiting", size_hint=(None, None))
        # vol_down_btn = Button(text="Waiting", size_hint=(None, None))
        
        
        #layout the objects
        padding_x = 5
        padding_y = 1
        
        btn_dim = 75
        btn_size = (btn_dim, btn_dim)
        
        play_btn.size = btn_size
        next_btn.size = btn_size
        prev_btn.size = btn_size
        
        play_btn.x = x + padding_x
        play_btn.center_y = center_y
        prev_btn.x = x + padding_x * 2 + btn_dim
        prev_btn.center_y = center_y
        next_btn.x = x + padding_x * 3 + btn_dim * 2
        next_btn.center_y = center_y
        
        # vol_up_btn.size = btn_size
        # vol_down_btn.size = btn_size
        # vol_up_btn.x = x + padding_x * 4 + btn_dim * 3
        # vol_up_btn.center_y = center_y
        # vol_down_btn.x = x + padding_x * 5 + btn_dim * 4
        # vol_down_btn.center_y = center_y
        
        
        data_x = x + padding_x * 4 + btn_dim * 3
        # data_x = x + padding_x * 6 + btn_dim * 5
        data_width = self.width - data_x
        text_height = 15
        time_width = 40
        slider_height = 30
        slider_center_y = top - padding_y * 4 - text_height * 3 - slider_height / 2.0
        
        title_label.pos = (data_x + padding_x, top - (padding_y + text_height) * 1)
        title_label.size = (data_width - 2 * padding_x, text_height)
        artist_label.pos = (data_x + padding_x, top - (padding_y + text_height) * 2)
        artist_label.size = (data_width - 2 * padding_x, text_height)
        album_label.pos = (data_x + padding_x, top - (padding_y + text_height) * 3)
        album_label.size = (data_width - 2 * padding_x, text_height)
        playtime_label.size = (time_width, text_height)
        playtime_label.x = data_x + padding_x
        playtime_label.center_y = slider_center_y
        length_label.size = (time_width, text_height)
        length_label.right = data_x + data_width - padding_x
        length_label.center_y = slider_center_y
        playback_slider.width = length_label.x - padding_x * 2 - playtime_label.right
        playback_slider.height = slider_height
        playback_slider.x = playtime_label.right + padding_x
        playback_slider.center_y = slider_center_y
        
        #add the objects
        self._add_widget(play_btn)
        self._add_widget(prev_btn)
        self._add_widget(next_btn)
        self._add_widget(title_label)
        self._add_widget(artist_label)
        self._add_widget(album_label)
        self._add_widget(playtime_label)
        self._add_widget(length_label)
        self._add_widget(playback_slider)
        
        
        playback_slider.bind(on_touch_up=self.slider_touch_up, on_touch_down=self.slider_touch_down)
        playback_slider.bind(value=self._update_playtime_label)
        play_btn.bind(on_press=self.play_pause_track)
        next_btn.bind(on_press=self.next_track)
        prev_btn.bind(on_press=self.prev_track)
        
        vol_up_btn.bind(on_press=self.vol_up)
        vol_down_btn.bind(on_press=self.vol_down)
        
        
        #store objects to self
        self.play_btn = play_btn
        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self.title_label = title_label
        self.artist_label = artist_label
        self.album_label = album_label
        self.playtime_label = playtime_label
        self.length_label = length_label
        self.playback_slider = playback_slider
        
        
        
        
        
    #external binding stuff
    # def bind_control_events(self, next=None, prev=None, play=None, seek=None)
    # def vol_up(self, inst):
    #     pass
    # 
    # def vol_down(self, inst):
    #     pass

    def next_track(self, inst):
        self.xmms.next()
        #TODO update data
    
    def prev_track(self, inst):
        self.xmms.prev()
        #TODO update data
    
    def play_pause_track(self, inst):
        state = self.state
        if state == "Paused":
            self.xmms.play()
        elif state == "Playing":
            self.xmms.pause()
    
    # def pause_track
    #handle xmms stuff
    def handle_xmms_connected(self):
        #local ref to xmms
        xmms = self.xmms
        
        #set data
        md = xmms.get_metadata_blocking()
        self.set_track_data(md)
        
        self.next_btn.text = "Next"
        self.prev_btn.text = "Prev"
        statuses = ["Stopped", "Playing", "Paused"]
        status = statuses[xmms.get_status_blocking()]
        if status == "Stopped" or status == "Paused":
            self.play_btn.text = "Play"
            self.state = "Paused"
        else:
            self.play_btn.text = "Pause"
            self.state = "Playing"
        
        #TODO get and set current playtime....
        xmms.get_playback_playtime(cb=self.update_playtime)
        
        xmms.register_playback_playtime_callback(self.update_playtime)
        xmms.register_playback_current_id_callback(self.current_id_cb)
        xmms.register_playback_status_callback(self.playback_state_changed)
        #TODO finish this
        # pass
    
    def handle_xmms_disconnected(self):
        self.title_label.text = "Waiting"
        self.artist_label.text = "Waiting"
        self.album_label.text = "Waiting"
        self.playtime_label.text = self._time_str(0)
        self.playback_slider.value = 0
        self.playback_slider.max = 0
        self.length_label.text = self._time_str(0)
        
        self.play_btn.text = "Waiting"
        self.next_btn.text = "Waiting"
        self.prev_btn.text = "Waiting"
        #TODO finish this
        # pass
        
    #handle track data stuff
    def set_track_data(self, data):
        # print "set_track_data ", data
        self.title_label.text = str(data['title'])
        self.artist_label.text = str(data['artist'])
        self.album_label.text = str(data['album'])
        # self.playtime_label.text = self._time_str(0)
        self.playback_slider.value = 0
        try: length = int(data['length'])
        except: length = int(data['duration'])
        self.playback_slider.max = length
        self.length_label.text = self._time_str(length)
        pass
    
    def current_id_cb(self, media_id):
        # print "current_id_cb ", media_id
        self.xmms.get_metadata(media_id, self.set_track_data)
    
    def update_playtime(self, time_ms):
        if not self.is_seeking:
            # print "update_playtime ", time_ms
            # self.playtime_label.text = self._time_str(time_ms)
            self.playback_slider.value = time_ms
            self.last_playtime = time_ms
            # pass
    
    def playback_state_changed(self, state):
        if state == "Stopped" or state == "Paused":
            self.play_btn.text = "Play"
            self.state = "Paused"
        else:
            self.play_btn.text = "Pause"
            self.state = "Playing"
    
    #handle events...
    def _update_playtime_label(self, inst, value):
        self.playtime_label.text = self._time_str(value)
    
    def slider_touch_down(self, obj, touch):
        if self.playback_slider.collide_point(*touch.pos):
            self.is_seeking = True
    
    def slider_touch_up(self, obj, touch):
        # self.is_seeking = True
        playback_slider = self.playback_slider
        value = playback_slider.value
        self.old_playtime = self.last_playtime
        #TODO make seek actually seek.....
        if self.is_seeking:# and playback_slider.collide_point(*touch.pos):
            if self.state == "Playing":
                seek_pos = int(value)
                print "seek to ", seek_pos
            
                def seek_cb(r):
                    print r
            
                try:
                    self.xmms.seek(seek_pos, cb=seek_cb)
                except SeekException as se:
                    print "can't seek if not playing so reseting slider to last playtime"
                    Clock.schedule_once(self._reset_slider_to_last_value, -1)
            else:
                Clock.schedule_once(self._reset_slider_to_last_value, -1)
        self.is_seeking = False
    
    def _reset_slider_to_last_value(self, dt=None):
        print "_reset_slider_to_last_value"
        self.playback_slider.value = self.old_playtime
    
    #no external control of children
    def add_widget(self, widget, index=0):
        raise Exception()
    
    def remove_widget(self, widget):
        raise Exception()
    
    def _add_widget(self, widget, index=0):
        # widget.bind(
        #     pos_hint=self._trigger_layout)
        return super(MediaBar2, self).add_widget(widget, index)

    def _remove_widget(self, widget):
        # widget.unbind(
        #     pos_hint=self._trigger_layout)
        return super(MediaBar2, self).remove_widget(widget)

    # class util functions
    def _time_str(self, time_ms):
        time = time_ms / 1000.0
        mins = int(floor(time / 60))
        secs = int(time - mins * 60)
        out = "%02d:%02d"%(mins, secs)
        return out
    # def _add_widget(self, widget, index=0):
    #     widget.bind(
    #         size=self._trigger_layout,
    #         size_hint=self._trigger_layout)
    #     return super(Layout, self).add_widget(widget, index)
    # 
    # def _remove_widget(self, widget):
    #     widget.unbind(
    #         size=self._trigger_layout,
    #         size_hint=self._trigger_layout)
    #     return super(Layout, self).remove_widget(widget)
    
    
    
class MediaBar(GridLayout):
    title_label = ObjectProperty(None)
    album_label = ObjectProperty(None)
    artist_label = ObjectProperty(None)
    playback_slider = ObjectProperty(None)
    next_btn = ObjectProperty(None)
    prev_btn = ObjectProperty(None)
    play_btn = ObjectProperty(None)
    seek_pos = NumericProperty(None)
    
    def time_str(self, time):
        mins = int(floor(time / 60))
        secs = int(time - mins * 60)
        out = "%02d:%02d"%(mins, secs)
        return out
    
    #setup methods
    def setup(self):
        # self.playback_slider.bind(on_touch_up=self.seek_to)
        # self.next_btn.bind(on_press=self.next_track)
        # self.prev_btn.bind(on_press=self.prev_track)
        # self.play_btn.bind(on_press=self.play_btn_pressed)
        
        self.state = None
        self.connected = False
        self.currently_playing = None
        
        xmms = XmmsConnection()
        xmms.connect_after('xmmsconnected', self.xmms_connected_cb)
        xmms.connect_after('xmmsdisconnected', self.xmms_disconnected_cb)
        self.xmms = xmms
        Clock.schedule_once(self.setup_xmmscon, 1)
    
    def setup_xmmscon(self, dt):
        print "setup_xmmscon"
        self.xmms.connect_to_xmms()

    #xmms connection callbacks
    def xmms_connected_cb(self, con_stat, data=None):
        print "xmms_connected_cb"
        xmms = self.xmms

        xmms.register_playback_status_callback(self.playback_status_cb)
        xmms.register_playback_current_id_callback(self.plaback_current_id_cb)
        xmms.register_playback_playtime_callback(self.playback_playtime_cb)

        status = xmms.get_status_blocking()
        currently_playing = xmms.get_metadata_blocking()
        self.currently_playing = currently_playing
        self.connected = True
        
        self.next_btn.text = "Next"
        self.prev_btn.text = "Prev"
        if status == "Stopped" or status == "Paused":
            state = "Paused"
            self.play_btn.text = "Play"
        else:
            state = "Playing"
            self.play_btn.text = "Pause"
        self.status = state
        
        #set the display state
        try:
            self.title_label.text = str(currently_playing['title'])
            self.album_label.text = str(currently_playing['album'])
            self.artist_label.text = str(currently_playing['artist'])
            self.playback_slider.value = 0
            self.playback_slider.max = float(currently_playing['length']) / 1000.0
        except KeyError:
            self.title_label.text = ""
            self.album_label.text = ""
            self.artist_label.text = ""
            self.playback_slider.max = 0
        
        self.playback_slider.bind(on_touch_up=self.seek_to)
        self.next_btn.bind(on_press=self.next_track)
        self.prev_btn.bind(on_press=self.prev_track)
        self.play_btn.bind(on_press=self.play_btn_pressed)
        

    def xmms_disconnected_cb(self, con_stat, data=None):
        print "xmms_disconnected_cb"
        self.connected = False
        self.status = None
        
        self.playback_slider.unbind(on_touch_up=self.seek_to)
        self.next_btn.unbind(on_press=self.next_track)
        self.prev_btn.unbind(on_press=self.prev_track)
        self.play_btn.unbind(on_press=self.play_btn_pressed)
        
        self.currently_playing = None
        self.next_btn.text = "Waiting"
        self.prev_btn.text = "Waiting"
        self.play_btn.text = "Waiting"
        self.title_label.text = ""
        self.album_label.text = ""
        self.artist_label.text = ""
        self.playback_slider.value = 0
        self.playback_slider.max = 0
        
        #TODO what else should be done if disconnected?
        
        
    #xmms plaback event callbacks
    def playback_status_cb(self, status):
        print "playback_status_cb: ", status
        if status == "Stopped" or status == "Paused":
            state = "Paused"
            self.play_btn.text = "Play"
        else:
            state = "Playing"
            self.play_btn.text = "Pause"
        
        self.status = state
        # pass
        
    def plaback_current_id_cb(self, media_id):
        print "plaback_current_id_cb: ", media_id
        #get metadata for media_id
        currently_playing = xmms.get_metadata_blocking(media_id)
        self.currently_playing = currently_playing
        #set the labels for the new info
        try:
            self.title_label.text = str(currently_playing['title'])
            self.album_label.text = str(currently_playing['album'])
            self.artist_label.text = str(currently_playing['artist'])
            self.playback_slider.value = 0
            self.playback_slider.max = float(currently_playing['length']) / 1000.0
        except KeyError:
            self.title_label.text = ""
            self.album_label.text = ""
            self.artist_label.text = ""
            self.playback_slider.max = 0
    
    def playback_playtime_cb(self, time_ms):
        print "playback_playtime_cb: ", time_ms
        self.playback_slider.value = float(time_ms) / 1000.0
    
    #GUI event handlers
    def play_btn_pressed(self, inst):
        print "play/pause btn pressed"
        if self.state == "Playing":
            self.play_btn.text = "pause"
            if self.connected:
                self.xmms.play()
        elif self.state == "Paused":
            self.play_btn.text = "play"
            if self.connected:
                self.xmms.pause()
    
    def seek_to(self, obj, touch):
        print "obj:    ", obj
        print "slider: ", self.playback_slider
        print "tounch: ", touch
        if obj is self.playback_slider:
            seek_pos = int(self.playback_slider.value * 1000)
            print "seek to ", seek_pos
            self.xmms.seek(seek_pos)
    
    def next_track(self, obj):
        if obj is self.next_btn:
            
            def next_cb(r):
                print "next_cb '", r, "'"
            
            self.xmms.next(cb=next_cb)
    
    def prev_track(self, obj):
        if obj is self.prev_btn:
            
            def prev_cb(r):
                print "prev_cb '", r, "'"
            
            self.xmms.prev(cb=prev_cb)
    
    # def set_playing(self, song):
    #     self.title_label.text = song['title']
    #     # self.album_label.text = song['album']
    #     self.artist_label.text = song['artist']
    #     self.playback_slider.value = 0
    #     self.playback_slider.max = song['length']


class TestxmmsApp(App):
    
    def xmms_connected_cb(self, con_stat, data=None):
        self.mb.handle_xmms_connected()
    
    def xmms_disconnected_cb(self, con_stat, data=None):
        self.mb.handle_xmms_disconnected()
    
    
    def setup_xmmscon(self, dt):
        print "setup_xmmscon"
        self.xmms.connect_to_xmms()

    def build(self):
        xmmscon = XmmsConnection()
        mb = MediaBar2(xmmscon)
        mb.x = 0
        mb.height = 80
        mb.width = 800
        mb.y = 480 - 80
        mb.setup_contents()
        xmmscon.connect_after('xmmsconnected', self.xmms_connected_cb)
        xmmscon.connect_after('xmmsdisconnected', self.xmms_disconnected_cb)
        Clock.schedule_once(self.setup_xmmscon, 15)
        
        self.xmms = xmmscon
        self.mb = mb
        return mb
        
        # mb = MediaBar()
        # mb.setup()
        # self.mediabar = mb
        # return mb
        
        # mv = MainView()#SongList()
        # mv.set_songs({
        # "a":{"title":"songa", "artist":"artista", "album":"albuma", "filename":"filea", "length": 123},
        # "b":{"title":"songb", "artist":"artistb", "album":"albumb", "filename":"fileb", "length": 234},
        # "c":{"title":"songc", "artist":"artistc", "album":"albumc", "filename":"filec", "length": 345},
        # "d":{"title":"songd", "artist":"artistd", "album":"albumd", "filename":"filed", "length": 456},
        # "e":{"title":"songe", "artist":"artiste", "album":"albume", "filename":"filee", "length": 567},
        # "f":{"title":"songf", "artist":"artistf", "album":"albumf", "filename":"filef", "length": 678}})
        # mv.setup()
        # return mv#sl
        # return MediaBar()
        # return PlaybackInfoWidget()
        
if __name__ == '__main__':
    TestxmmsApp().run()
    # interactiveLauncher = InteractiveLauncher(TestxmmsApp()).run()