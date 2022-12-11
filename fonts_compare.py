#!/usr/bin/python3
'''
This is my fonts-compare program for font rendering and comparing
'''
from typing import Any
from typing import List
import sys
import os
import random
import re
import subprocess
import shutil
import locale
import argparse
import logging
import unicodedata
import langtable # type: ignore
import langdetect # type: ignore
import gi # type: ignore
# pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk # type: ignore
from gi.repository import Gio, GLib # type: ignore
gi.require_version('Pango', '1.0')
from gi.repository import Pango
# pylint: enable=wrong-import-position

LOGGER = logging.getLogger('fonts-compare')

def parse_args() -> Any:
    '''Parse the command line arguments'''
    parser = argparse.ArgumentParser(
            description='fonts-compare program')
    parser.add_argument(
            '-d', '--debug',
            action='store_true',
            default=False,
            help=('Print debug output '
                  'default: %(default)s'))
    return parser.parse_args()

_ARGS = parse_args()

FALLPARAM = 'fallback="false">'
FONTSIZE = '40'
LABEL3_FONT = '20'

class FontsCompareAboutDialog(Gtk.AboutDialog): # type: ignore
    '''
    The “About” dialog for fonts-compare
    '''
    def  __init__(self, parent: Gtk.Window = None) -> None:
        Gtk.AboutDialog.__init__(self, parent=parent)
        self.set_modal(True)
        # An empty string in aboutdialog.set_logo_icon_name('')
        # prevents an ugly default icon to be shown. We don’t yet
        # have nice icons for Fonts Compare
        self.set_logo_icon_name('help-about-symbolic')
        self.set_title('Fonts Compare')
        self.set_program_name('Fonts Compare')
        self.set_version('1.0.6')
        self.set_comments('A tool to compare fonts.')
        self.set_copyright(
            'Copyright © 2022 Sudip Shil')
        self.set_authors([
            'Sudip Shil <sudipshil9862@gmail.com>',
            ])
        self.set_translator_credits(
            # Translators: put your names here, one name per line.
            #_('translator-credits')
            'Nobody translated anything yet.'
        )
        # self.set_artists('')
        self.set_documenters([
            'Sudip Shil sudipshil9862@gmail.com',
            ])
        self.set_website(
            'https://github.com/sudipshil9862/fonts-compare')
        self.set_website_label(
            'Github: https://github.com/sudipshil9862/fonts-compare')
        self.set_license('''
        No license decided yet.
        ''')
        self.set_wrap_license(True)
        # overrides the above .set_license()
        #self.set_license_type(Gtk.License.GPL_3_0)
        self.connect('close-request', self._on_close_aboutdialog)
        if parent:
            self.set_transient_for(parent.get_toplevel())
        self.show()

    def _on_close_aboutdialog( # pylint: disable=no-self-use
            self,
            _about_dialog: Gtk.Dialog,
            ) -> None:
        '''
        The “About” dialog has been closed by the user

        :param _about_dialog: The “About” dialog
        :param _response: The response when the “About” dialog was closed
        '''
        self.destroy()


MENU_HAMBURGER_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="label" translatable="yes">Use Pango Sample Text</attribute>
        <attribute name="action">win.radio</attribute>
        <attribute name="target">PangoSampleText</attribute>
      </item>
      <item>
        <attribute name="action">win.about</attribute>
        <attribute name="label" translatable="yes">_About</attribute>
      </item>
      <item>
        <attribute name="action">win.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;Q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""

class AppWindow(Gtk.ApplicationWindow): # type: ignore
    '''
    Including appwindow class to window to present
    '''
    def __init__(self, appp: Gtk.Application) -> None:
        super().__init__(application=appp)
        self.init_ui()

    def init_ui(self) -> None:
        '''
        init_ui contains all the containers, labels, buttons
        '''
        self.set_title('Font Compare')

        header_bar = Gtk.HeaderBar()
        header_bar.set_hexpand(True)
        header_bar.set_vexpand(False)

        quit_action = Gio.SimpleAction.new("quit", None) # look at MENU_XML win.quit
        quit_action.connect("activate", self._on_quit_button_clicked)
        self.add_action(quit_action) # (self window) == win in MENU_XML

        about_action = Gio.SimpleAction.new("about", None) # look at MENU_XML win.about
        about_action.connect("activate", self._on_about_button_clicked)
        self.add_action(about_action) # (self window) == win in MENU_XML

        radio_action = Gio.SimpleAction.new_stateful('toggle',
                                                     GLib.VariantType.new('b'),
                                                     GLib.Variant('b', False))
        radio_action = Gio.SimpleAction.new_stateful('radio',
                                                     GLib.VariantType.new('s'),
                                                     GLib.Variant('s', 'PangoSampleText'))
        radio_action.connect('activate', lambda action,
                             target: print('toggling radio action to', target.get_string()) or
                             action.change_state(target))
        #radio_action.connect('activate', radio_button_on_connect())
        self.add_action(radio_action)

        self.menu_button = Gtk.MenuButton.new()
        header_bar.pack_end(self.menu_button) # or pack_end
        #use pango sample text checkbox
        #pango_sampletext_checkbox = Gtk.CheckButton.new_with_label('Use Pango Sample Text')
        #pango_sampletext_checkbox.set_active(False)
        #pango_sampletext_checkbox.connect('toggled', self.switch_switched)
        #about,quit
        menu = Gtk.Builder.new_from_string(MENU_HAMBURGER_XML, -1).get_object("app-menu")
        self.menu_button.set_icon_name("open-menu-symbolic") # from Pre-installed standard linux icon names
        #self.menu_button.set_menu_model(pango_sampletext_checkbox)

        self.menu_button.set_menu_model(menu)

        #----------------------------
        '''
        main = Gio.Menu.new()
        #header_bar.pack_end(main) # or pack_end
        lang_menuitem = Gio.MenuItem.new('Language')
        menu = Gio.Menu.new()
        #select_lang_menuitem = Gio.MenuItem.new('Select Language', 'app.change_language')
        select_lang_menuitem = Gio.MenuItem.new('Select Language')
        menu.append_item(select_lang_menuitem)
        lang_menuitem.set_submenu(menu)
        main.append_item(lang_menuitem)
        app.set_menubar(main)
        self.set_show_menubar(True)
        '''
        #----------------------------

        #--------------------------
        main_menu_button = Gtk.MenuButton()
        main_menu_button.set_icon_name("open-menu-symbolic")
        main_menu_button.set_direction(Gtk.ArrowType.DOWN)
        #header_bar.pack_start(main_menu_button)
        header_bar.pack_end(main_menu_button)
        self._main_menu_popover = Gtk.Popover()
        main_menu_button.set_popover(self._main_menu_popover)
        self._main_menu_popover.set_autohide(True)
        self._main_menu_popover.set_position(Gtk.PositionType.BOTTOM)
        main_menu_popover_vbox = Gtk.Box()
        main_menu_popover_vbox.set_orientation(Gtk.Orientation.VERTICAL)
        main_menu_popover_vbox.set_spacing(0)

        #sample text toggle button in header bar
        self._sampletext_toggle_button = Gtk.MenuButton(label='sample text')
        #self._sampletext_toggle_button.set_has_tooltip(True)
        #self._sampletext_toggle_button.set_tooltip_text('Select language')
        self._sampletext_toggle_button.set_direction(Gtk.ArrowType.DOWN)
        #header_bar.pack_start(self._sampletext_toggle_button)
        main_menu_popover_vbox.append(self._sampletext_toggle_button)
        self._sampletext_toggle_button_popover = Gtk.Popover()
        self._sampletext_toggle_button.set_popover(self._sampletext_toggle_button_popover)
        self._sampletext_toggle_button_popover.set_autohide(True)
        self._sampletext_toggle_button_popover.set_position(Gtk.PositionType.BOTTOM)
        #self._sampletext_toggle_button_popover.set_vexpand(True)
        #self._sampletext_toggle_button_popover.set_hexpand(True)
        self._sampletext_toggle_button_popover_hbox = Gtk.Box()
        self._sampletext_toggle_button_popover_hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._sampletext_toggle_button_popover_hbox.set_spacing(0)
        #self.label_switch_prev_langtable = Gtk.Label(label = 'LangTable')
        #self.label_switch_next_pango = Gtk.Label(label = 'Pango')
        self.label_switch_select_pango_text = Gtk.Label(label = 'Use Pango Sample Text')
        self.switch_sample_text = Gtk.Switch()
        self.switch_sample_text.set_active(False)
        self.switch_sample_text.connect("state-set", self.switch_switched)
        #self._sampletext_toggle_button_popover_hbox.append(self.label_switch_prev_langtable)
        self._sampletext_toggle_button_popover_hbox.append(self.label_switch_select_pango_text)
        self._sampletext_toggle_button_popover_hbox.append(self.switch_sample_text)
        #self._sampletext_toggle_button_popover_hbox.append(self.label_switch_next_pango)
        self._sampletext_toggle_button_popover.set_child(self._sampletext_toggle_button_popover_hbox)

        self._main_menu_about_button = Gtk.Button(label='About')
        self._main_menu_about_button.connect(
            'clicked', self._on_about_button_clicked)
        main_menu_popover_vbox.append(self._main_menu_about_button)
        self._main_menu_quit_button = Gtk.Button(label='Quit')
        self._main_menu_quit_button.connect('clicked', self._on_quit_button_clicked)
        main_menu_popover_vbox.append(self._main_menu_quit_button)

        self._main_menu_popover.set_child(main_menu_popover_vbox)

        #---------------------------

        self._language_menu_button = Gtk.MenuButton(label='Use language en')
        self._language_menu_button.set_has_tooltip(True)
        self._language_menu_button.set_tooltip_text('Use language')
        self._language_menu_button.set_direction(Gtk.ArrowType.DOWN)
        header_bar.pack_start(self._language_menu_button)
        self._language_menu_popover = Gtk.Popover()
        self._language_menu_button.set_popover(self._language_menu_popover)
        self._language_menu_popover.set_autohide(True)
        self._language_menu_popover.set_position(Gtk.PositionType.BOTTOM)
        self._language_menu_popover.set_vexpand(True)
        self._language_menu_popover.set_hexpand(True)
        self._language_menu_popover_scroll = Gtk.ScrolledWindow()
        self._language_menu_popover_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self._language_menu_popover_scroll.set_has_frame(True)
        self._language_menu_popover_scroll.set_hexpand(True)
        self._language_menu_popover_scroll.set_vexpand(True)
        # set_propagate_natural_height(True) is important, otherwise the
        # scrolled window will be very short (only two rows will did fit):
        self._language_menu_popover_scroll.set_propagate_natural_height(True)
        self._language_menu_popover_scroll.set_valign(Gtk.Align.FILL)
        self._language_menu_popover_scroll.set_kinetic_scrolling(False)
        self._language_menu_popover_scroll.set_overlay_scrolling(True)
        self._language_menu_popover.connect(
            'show', self._on_language_menu_popover_show)
        self._language_menu_popover_language_ids: List[str] = []

        self.set_titlebar(header_bar)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.props.halign = Gtk.Align.CENTER
        self.vbox.set_margin_top(25)

        self.vbox_labels = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox_labels.props.halign = Gtk.Align.CENTER
        self.vbox_labels.set_spacing(0)

        self.hbox_button2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox_button2.set_margin_top(10)
        self.hbox_button2.props.halign = Gtk.Align.CENTER

        self.vbox_last = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox_last.set_margin_top(0)
        self.vbox_last.set_margin_bottom(20)
        self.vbox_last.props.halign = Gtk.Align.CENTER

        self.vbox_error_note = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox_error_note.set_margin_top(20)
        self.vbox_error_note.set_margin_bottom(20)
        self.vbox_error_note.props.halign = Gtk.Align.CENTER

        self.hbox1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox1.set_margin_top(10)
        self.hbox1.props.halign = Gtk.Align.CENTER

        self.hbox2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox2.set_margin_top(10)
        self.hbox2.props.halign = Gtk.Align.CENTER

        self.hbox3 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox3.set_margin_top(10)
        self.hbox3.props.halign = Gtk.Align.CENTER

        self.hbox4 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox4.set_margin_top(10)
        self.hbox4.props.halign = Gtk.Align.CENTER

        self.hbox_adjustment = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox_adjustment.set_margin_top(10)
        self.hbox_adjustment.props.halign = Gtk.Align.CENTER


        self.hbox_entry_label = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox_entry_label.set_margin_top(10)


        self.entry = Gtk.Entry()
        self.label_entry_define = Gtk.Label(label="  Type Here")
        self.label3 = Gtk.Label(label="")
        self.hbox_entry_label.append(self.label_entry_define)
        self.vbox.append(self.hbox_entry_label)
        self.vbox.append(self.entry)
        self.vbox.append(self.label3)
        '''
        self.combo = Gtk.ComboBoxText()
        self.label4 = Gtk.Label()
        self.label4.set_markup('<span font="'+self.get_default_font_family_for_language('en')
                               +' '+'15'+'"' + FALLPARAM
                               + 'Select Language'
                               + '</span>')
        self.hbox3.append(self.label4)
        self.hbox3.append(self.combo)
        self.vbox.append(self.hbox3)
        '''
        self.label_error = Gtk.Label()
        self.vbox_error_note.append(self.label_error)
        self.vbox.append(self.vbox_error_note)

        #switch button/toggle button - pango and langtable sample string - sample text
        '''
        self.label5 = Gtk.Label()
        self.label5.set_markup('<span font="'+self.get_default_font_family_for_language('en')
                               +' '+'15'+'"' + FALLPARAM
                               + ' Use Sample Text :  '
                               + '</span>')
        self.hbox4.append(self.label5)
        self.label_switch_prev = Gtk.Label(label = 'LangTable')
        self.label_switch_next = Gtk.Label(label = 'Pango')
        self.switch = Gtk.Switch()
        self.switch.set_active(False)
        self.switch.connect("state-set", self.switch_switched)
        self.hbox4.append(self.label_switch_prev)
        self.hbox4.append(self.switch)
        self.hbox4.append(self.label_switch_next)
        self.vbox.append(self.hbox4)
        '''

        self.label1 = Gtk.Label()
        self.button1 = Gtk.FontButton.new()
        self.fontbutton(self.label1, self.button1, self.hbox1)
        self.vbox.append(self.hbox1)
        #self.vbox.append(self.label1)
        self.vbox_labels.append(self.label1)
        self.label2 = Gtk.Label()
        self.button2 = Gtk.FontButton.new()
        self.fontbutton(self.label2, self.button2, self.hbox_button2)
        #self.vbox.append(self.label2)
        self.vbox_labels.append(self.label2)
        self.vbox.append(self.vbox_labels)
        self.vbox_last.append(self.hbox_button2)
        self.vbox.append(self.vbox_last)
        temp_random_font = self.get_random_font_family_for_language('en')
        self.label2.set_markup('<span font="'+temp_random_font
                               +' '+FONTSIZE+'"' + FALLPARAM
                               + self.sample_text_selector('en')
                               + '</span>')
        self.button2.set_font(temp_random_font + ' ' + FONTSIZE)

        #first initialize text of label1 set to entry textbox
        self.entry.set_text(self.label1.get_text())
        self.entry.set_position(-1)
        self.entry.changed_signal_id = self.entry.connect(
            'notify::text', self.on_entry_changed)

        #wrap text
        #self.label1.set_wrap(True)
        #self.label2.set_wrap(True)

        '''
        #slider for both label-font change
        self.slider = Gtk.Scale()
        self.slider.set_digits(0)
        self.slider.set_range(1,100)
        self.slider.set_draw_value(True)
        self.slider.set_value(int(FONTSIZE)) #default fontsize that initialized globally
        self.button1_family = ''
        self.button2_family = ''
        self.slider.connect('value-changed', self.slider_changed,
                            self.button1_family, self.button2_family)
        '''
        self.label_slider = Gtk.Label()
        self.label_slider.set_markup('<span font="'+self.get_default_font_family_for_language('en')
                                     +' '+'12'+'"' + FALLPARAM
                                     + '\nSelect FontSize'
                                     + '</span>')
        #self.vbox_last.append(self.slider)

        #jft - increment decrement widget font size
        self._fontsize_spin_button = Gtk.SpinButton()
        self._fontsize_spin_button.set_numeric(True)
        self._fontsize_spin_button.set_can_focus(True)
        self._fontsize_spin_button.set_tooltip_text('Set font size')
        self._fontsize_adjustment = Gtk.Adjustment()
        self._fontsize_adjustment.set_lower(1)
        self._fontsize_adjustment.set_upper(100)
        self._fontsize_adjustment.set_value(int(FONTSIZE))
        self._fontsize_adjustment.set_step_increment(1)
        self._fontsize_spin_button.set_adjustment(self._fontsize_adjustment)
        self.button1_family = ''
        self.button2_family = ''
        self._fontsize_adjustment.connect(
            'value-changed', self.on_fontsize_adjustment_value_changed, self.button1_family, self.button2_family)
        self.hbox_adjustment.append(self._fontsize_spin_button)
        self.vbox_last.append(self.label_slider)
        self.vbox_last.append(self.hbox_adjustment)


        '''
        list_dropdown.sort()
        for lang in list_dropdown:
            self.combo.append_text(lang)
        # Make 'en' active by default to avoid seeing an empty
        # assume that and just search for 'en' whereever it is):
        for i, item in enumerate(self.combo.get_model()):
            if item[0] == 'en':
                self.combo.set_active(i)
        self.combo.changed_signal_id = self.combo.connect('changed', self.on_changed)
        '''

        text = self.label1.get_text()
        lang = self.detect_language(text)
        LOGGER.info('label1: text=%s lang=%s', text,lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup(
                f'<span font="{self.get_default_font_family_for_language(lc_messages_lang)} '
                f'{LABEL3_FONT}" {FALLPARAM}{label_lang_full_form}</span>')

        self.set_resizable(True)
        self.set_child(self.vbox)

        self.entry.grab_focus_without_selecting()

    #spin button font size change by adjustment increment decrement
    def on_fontsize_adjustment_value_changed(
            self,
            adjustment: Gtk.Adjustment,
            button1_family: str,
            button2_family: str) -> None:
        value = adjustment.get_value()
        if _ARGS.debug:
            LOGGER.debug(
                'on_fontsize_adjustment_value_changed() value = %s\n', value)
        #both text labels will change it's fontsize depending upon adjustment increment decrement widget
        button1_family = self.button1.get_font().rsplit(' ',1)[0]
        button2_family = self.button2.get_font().rsplit(' ',1)[0]
        self.button1.set_font(button1_family + ' ' + str(self._fontsize_adjustment.get_value()))
        self.button2.set_font(button2_family + ' ' + str(self._fontsize_adjustment.get_value()))
        '''
        self.label1.set_markup('<span font="'+self.button1.get_font()+'"' + FALLPARAM
                               + self.label1.get_text()
                               + '</span>')
        self.label2.set_markup('<span font="'+self.button2.get_font()+'"' + FALLPARAM
                               + self.label2.get_text()
                               + '</span>')
        '''
        self.label1.set_markup('<span font="'+button1_family+' '+str(self._fontsize_adjustment.get_value())+'"' + FALLPARAM
                               + self.label1.get_text()
                               + '</span>')
        self.label2.set_markup('<span font="'+button2_family+' '+str(self._fontsize_adjustment.get_value())+'"' + FALLPARAM
                               + self.label2.get_text()
                               + '</span>')

        #LOGGER.info('slider_changed: button{1,2} font = %s', str(int(slider.get_value())))
        #wrapping text if font size greater than 40
        if int(self._fontsize_adjustment.get_value()) > 50:
            self.label1.set_wrap(True)
            self.label2.set_wrap(True)


    def fontbutton(
            self,
            label: Gtk.Label,
            button: Gtk.FontButton,
            boxh: Gtk.Box) -> None:
        '''
        setting up initial font and text for labels and font button text updated
        '''
        temp_label_button_font = self.get_default_font_family_for_language('en')
        label.set_markup('<span font="'+temp_label_button_font
                         +' '+FONTSIZE+'"' + FALLPARAM
                         + self.sample_text_selector('en')
                         + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(temp_label_button_font + ' ' + FONTSIZE)
        boxh.append(button)

    def switch_switched(
            self,
            _switch: Gtk.Switch,
            state: bool) -> None:
        '''
        function to change sample string depends upon toogle switch
        '''
        LOGGER.info('The switch has been switched %s', 'on' if state else 'off')
        global FONTSIZE
        if state:
            #True - sample_text by Pango.Language
            self.switch_sample_text.set_state(state)
            FONTSIZE = '20'
            LOGGER.info('pango font = %s',FONTSIZE)
            #instant label1 and label2 change after switch change
            self.label1.set_markup('<span font="'+self.button1.get_font().rsplit(' ',1)[0]
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(self._language_menu_button.get_label())
                                   + '</span>')
            self.button1.set_font(self.button1.get_font().rsplit(' ',1)[0] + ' ' + FONTSIZE)
            self.label2.set_markup('<span font="'+self.button2.get_font().rsplit(' ',1)[0]
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(self._language_menu_button.get_label())
                                   + '</span>')
            self.button2.set_font(self.button2.get_font().rsplit(' ',1)[0] + ' ' + FONTSIZE)
            #self.slider.set_value(int(FONTSIZE))
            self._fontsize_adjustment.set_value(int(FONTSIZE))
        else:
            #False - sample_text by langtable.language_name
            FONTSIZE = '40'
            self.switch_sample_text.set_state(state)
            LOGGER.info('langtable font = %s',FONTSIZE)
            #instant label1 and label2 change after switch change
            self.label1.set_markup('<span font="'+self.button1.get_font()
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(self._language_menu_button.get_label())
                                   + '</span>')
            self.label2.set_markup('<span font="'+self.button2.get_font()
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(self._language_menu_button.get_label())
                                   + '</span>')
            #self.slider.set_value(int(FONTSIZE))
            self._fontsize_adjustment.set_value(int(FONTSIZE))
        self.entry.handler_block(self.entry.changed_signal_id)
        self.entry.set_text(self.label1.get_text())
        self.entry.set_position(-1)
        self.entry.grab_focus_without_selecting()
        self.entry.handler_unblock(self.entry.changed_signal_id)



    def sample_text_selector(self, lang: str) -> str:
        '''
        sample text will be selected by either Pango or Langtable
        '''
        if self.switch_sample_text.get_state():
            #True - Pango sample text
            sample_text = str(Pango.Language.get_sample_string(
            Pango.language_from_string (lang)))
            return sample_text
        #False - Langtable sample text
        sample_text = str(langtable.language_name(
        languageId=lang, languageIdQuery=lang))
        return sample_text

    '''
    def slider_changed(
            self,
            slider: Gtk.Scale,
            button1_family: str,
            button2_family: str) -> None:
        #Called when the slider is moved
        #both text labels will change it's fontsize depending upon font's slider

        button1_family = self.button1.get_font().rsplit(' ',1)[0]
        button2_family = self.button2.get_font().rsplit(' ',1)[0]
        self.button1.set_font(button1_family + ' ' + str(int(slider.get_value())))
        self.button2.set_font(button2_family + ' ' + str(int(slider.get_value())))
        self.label1.set_markup('<span font="'+button1_family+' '+str(int(slider.get_value()))+'"' + FALLPARAM
                               + self.label1.get_text()
                               + '</span>')
        self.label2.set_markup('<span font="'+button2_family+' '+str(int(slider.get_value()))+'"' + FALLPARAM
                               + self.label2.get_text()
                               + '</span>')

        #LOGGER.info('slider_changed: button{1,2} font = %s', str(int(slider.get_value())))
        #wrapping text if font size greater than 40
        if int(slider.get_value()) > 40:
            self.label1.set_wrap(True)
            self.label2.set_wrap(True)
    '''

    @classmethod
    def label_font_change(
            cls, button: Gtk.FontButton, label: Gtk.Label) -> None:
        '''
        font family and font size changes by font-button dialog
        '''
        pango_font_description = Pango.FontDescription.from_string(str=button.get_font(),)
        pango_attr_font_desc = Pango.AttrFontDesc.new(desc=pango_font_description,)
        pango_attr_list = Pango.AttrList.new()
        pango_attr_list.insert(attr=pango_attr_font_desc)
        label.set_attributes(attrs=pango_attr_list)

    def set_font(self, detect_lang: str, set_text: str) -> None:
        '''
        setting up text,
        font family depending upon which language has detected
        '''
        temp_label1_font = self.get_default_font_family_for_language(detect_lang)
        self.label1.set_markup('<span font="'+temp_label1_font
                               +' '+str(int(self._fontsize_adjustment.get_value()))+'"' + FALLPARAM
                               + set_text + '</span>')
        LOGGER.info('self.button1.set_font(%s)',
                    temp_label1_font +' '+str(int(self._fontsize_adjustment.get_value())))
        self.button1.set_font(temp_label1_font +' '+str(int(self._fontsize_adjustment.get_value())))
        LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
        temp_label2_font = self.get_random_font_family_for_language(detect_lang)
        self.label2.set_markup('<span font="'+temp_label2_font
                               +' '+str(int(self._fontsize_adjustment.get_value()))+'"' + FALLPARAM
                               + set_text + '</span>')
        LOGGER.info('self.button2.set_font(%s)',
                    temp_label2_font +' '+ str(int(self._fontsize_adjustment.get_value())))
        self.button2.set_font(temp_label2_font +' '+ str(int(self._fontsize_adjustment.get_value())))
        LOGGER.info('self.button2.get_font(%s)',self.button2.get_font())

    '''
    def _on_about_button_clicked(self, _button: Gtk.Button) -> None:
        #The “About” button has been clicked
        LOGGER.debug('About button clicked')
        self._main_menu_popover.popdown()
        FontsCompareAboutDialog()
    '''

    def _on_about_button_clicked(self, _action: Gio.SimpleAction, _menubutton: Gtk.MenuButton) -> None:
        '''The “About” button has been clicked'''
        LOGGER.debug('About button clicked')
        #self._main_menu_popover.popdown()
        FontsCompareAboutDialog()

    '''
    def _on_quit_button_clicked(self, _button: Gtk.Button) -> None:
        #The “Quit” button has been clicked
        LOGGER.debug('Quit button clicked')
        #self._main_menu_popover.popdown()
        # Destroy all the windows bound to the GtkApplication
        # instance. Once the last window is destroyed, the application
        # will automatically terminate.
        self.destroy()
    '''

    def _on_quit_button_clicked(self, _action: Gio.SimpleAction, _menubutton: Gtk.MenuButton) -> None:
        '''The “Quit” button has been clicked'''
        LOGGER.debug('Quit button clicked')
        # Destroy all the windows bound to the GtkApplication
        # instance. Once the last window is destroyed, the application
        # will automatically terminate.
        self.destroy()

    def _on_language_search_entry_changed(
            self, search_entry: Gtk.SearchEntry) -> None:
        '''Called when the text in the language search entry changes'''
        LOGGER.debug('Language search entry changed')
        filter_text = search_entry.get_text()
        self._language_menu_popover_listbox_fill(filter_text)

    def _language_menu_popover_listbox_fill_row(self, language_id: str) -> str:
        '''Formats the text of a line in the listbox of languages'''
        row = language_id
        if is_right_to_left_messages():
             # Add U+200F RIGHT_TO_LEFT MARK
            row = chr(0x200F) + language_id
        language_description = locale_language_description(language_id)
        if language_description:
            row += ' ' + language_description
        return row

    def _language_menu_popover_listbox_fill(self, filter_text: str) -> None:
        '''Fill the list of languages to choose from'''
        LOGGER.debug('Filling list of languages to choose from')
        self._language_menu_popover_language_ids = []
        if self._language_menu_popover_scroll is None:
            LOGGER.debug('self._language_menu_popover_scroll is None')
            return
        listbox = Gtk.ListBox()
        listbox.set_vexpand(True)
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.set_activate_on_single_click(True)
        rows = []
        filter_words = remove_accents(filter_text.lower()).split()
        for language_id in sorted(list_languages()):
            text_to_match = locale_text_to_match(language_id)
            filter_match = True
            for filter_word in filter_words:
                if filter_word not in text_to_match:
                    filter_match = False
            if filter_match:
                self._language_menu_popover_language_ids.append(language_id)
                rows.append(
                    self._language_menu_popover_listbox_fill_row(language_id))
        for row in rows:
            label = Gtk.Label()
            label.set_text(row)
            label.set_xalign(0)
            margin = 1
            label.set_margin_start(margin)
            label.set_margin_end(margin)
            label.set_margin_top(margin)
            label.set_margin_bottom(margin)
            listbox.append(label)
        listbox.connect(
            'row-selected',
            self._on_language_menu_popover_listbox_row_selected)
        self._language_menu_popover_scroll.set_child(listbox)

    def _on_language_menu_popover_listbox_row_selected(
            self, _listbox: Gtk.ListBox, listbox_row: Gtk.ListBoxRow) -> None:
        '''Called when a language is selected'''
        LOGGER.debug('Listbox row selected')
        if not listbox_row:
            return
        index = listbox_row.get_index()
        language_id = self._language_menu_popover_language_ids[index]
        self._language_menu_popover.popdown()
        self._language_menu_button.set_label(language_id)
        self._language_menu_popover_language_ids = []
        LOGGER.info('language selected from menu = %s', language_id)
        text = self.sample_text_selector(language_id)
        self.entry.handler_block(self.entry.changed_signal_id)
        self.entry.set_text(text)
        self.entry.set_position(-1)
        self.entry.grab_focus_without_selecting()
        self.entry.handler_unblock(self.entry.changed_signal_id)
        #set_preview_text means -
        #Setting the sample text for specific selected language
        #into the sample text field section at the bottom of the Gtk font selection dialog
        self.button1.set_preview_text(text)
        self.button2.set_preview_text(text)
        self.set_font(language_id, text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=language_id,
                languageIdQuery=lc_messages)
        LOGGER.debug('label_lang_full_form=%s', label_lang_full_form)
        LOGGER.debug('label3 local lang=%s, label3 font=%s',
                     lc_messages_lang, self.get_default_font_family_for_language(lc_messages_lang))
        self.label3.set_markup('<span font="'+self.get_default_font_family_for_language(lc_messages_lang)
                               +' '+LABEL3_FONT+'"' + FALLPARAM
                               + label_lang_full_form + '</span>')
        '''
        self.combo.handler_block(self.combo.changed_signal_id)
        for index, item in enumerate(self.combo.get_model()):
            if item[0] == language_id:
                self.combo.set_active(index)
        self.combo.handler_unblock(self.combo.changed_signal_id)
        '''

    def _on_language_menu_popover_show(self, popover: Gtk.Popover) -> None:
        '''Called when the language menu popover is shown'''
        LOGGER.debug('Language menu popover is shown')
        if popover is None:
            LOGGER.error('popover is None, should never happen')
            return
        vbox = Gtk.Box()
        vbox.set_orientation(Gtk.Orientation.VERTICAL)
        margin = 12
        vbox.set_margin_start(margin)
        vbox.set_margin_end(margin)
        vbox.set_margin_top(margin)
        vbox.set_margin_bottom(margin)
        vbox.set_spacing(margin)
        label = Gtk.Label()
        label.set_text('Select language')
        label.set_halign(Gtk.Align.FILL)
        vbox.append(label)
        search_entry = Gtk.SearchEntry()
        search_entry.set_can_focus(True)
        search_entry.set_halign(Gtk.Align.FILL)
        vbox.append(search_entry)
        search_entry.connect(
            'search-changed', self._on_language_search_entry_changed)
        self._language_menu_popover_listbox_fill('')
        if self._language_menu_popover_scroll.get_parent():
            # self._language_menu_popover_scroll has already been
            # added to another vbox in a previous call to this
            # function remove it from there to be able to reparent it:
            self._language_menu_popover_scroll.get_parent().remove(
                self._language_menu_popover_scroll)
        # Set both scrollbars to their lowest values:
        hadjustment = self._language_menu_popover_scroll.get_hadjustment()
        hadjustment.set_value(hadjustment.get_lower())
        vadjustment = self._language_menu_popover_scroll.get_vadjustment()
        vadjustment.set_value(vadjustment.get_lower())
        vbox.append(self._language_menu_popover_scroll)
        popover.set_child(vbox)

    def on_entry_changed(self, widget: Gtk.Entry, _property_spec: Any) -> None:
        '''Called when the text in the entry has changed.

        While typing on gtk entry box, the language is detected
        automatically time and then the font family and fontsize to
        display the text on label3 is changed accordingly.
        '''
        text = widget.get_text()
        lang = self.detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        LOGGER.info('label_lang full form=%s',label_lang_full_form)
        self.label3.set_markup('<span font="'
                               +self.get_default_font_family_for_language(lc_messages_lang)
                               +' '+LABEL3_FONT+'"' + FALLPARAM
                               + label_lang_full_form + '</span>')
        if lang in list_dropdown:
            self.button1.set_preview_text(langtable.language_name(
                languageId=lang, languageIdQuery=lang))
            self.button2.set_preview_text(langtable.language_name(
                languageId=lang, languageIdQuery=lang))
            self.set_font(lang, text)
            self._language_menu_button.set_label(lang)
            '''
            self.combo.handler_block(self.combo.changed_signal_id)
            for i, item in enumerate(self.combo.get_model()):
                if item[0] == lang:
                    self.combo.set_active(i)
            self.combo.handler_unblock(self.combo.changed_signal_id)
            '''
        elif not lang in list_dropdown:
            LOGGER.info('%s is not there in dropdown list',label_lang_full_form)
            self.label1.set_markup('<span font="'
                                   +self.get_default_font_family_for_language(lang)
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + text + '</span>')
            LOGGER.info('self.button1.set_font(%s)',
                        self.get_default_font_family_for_language(lang)
                        +' '+FONTSIZE)
            self.button1.set_font(
                    self.get_default_font_family_for_language(lang)
                    +' '+FONTSIZE)
            LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
            self.label2.set_markup('<span font="'
                                   +self.get_default_font_family_for_language(lang)
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + text + '</span>')
            LOGGER.info('self.button2.set_font(%s)',
                        self.get_default_font_family_for_language(lang)
                        +' '+ FONTSIZE)
            self.button2.set_font(
                    self.get_default_font_family_for_language(lang)
                    +' '+ FONTSIZE)
            LOGGER.info('self.button2.get_font(%s)',self.button2.get_font())

    def on_changed(self, wid: Gtk.ComboBoxText) -> None:
        '''
        when we select a perticular langugage from the drop-down..
        if it's bengali then take one bengali text,
        setting up bengali fonts on set_font function,
        display the language full form in label3 depends upon
        which is the default langugage for the user have
        '''
        lang = wid.get_active_text()
        LOGGER.info('%s is selected from drop-down',lang)
        self._language_menu_button.set_label(lang)
        LOGGER.info('%s is selected from header bar language list',self._language_menu_button.get_label())
        text = self.sample_text_selector(lang)
        self.entry.handler_block(self.entry.changed_signal_id)
        self.entry.set_text(text)
        self.entry.set_position(-1)
        self.entry.grab_focus_without_selecting()
        self.entry.handler_unblock(self.entry.changed_signal_id)
        #set_preview_text means -
        #Setting the sample text for specific selected language
        #into the sample text field section at the bottom of the Gtk font selection dialog
        self.button1.set_preview_text(text)
        self.button2.set_preview_text(text)
        self.set_font(lang, text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang,
                languageIdQuery=lc_messages)
        LOGGER.debug('label_lang_full_form=%s', label_lang_full_form)
        LOGGER.debug('label3 local lang=%s, label3 font=%s',
                     lc_messages_lang, self.get_default_font_family_for_language(lc_messages_lang))
        self.label3.set_markup('<span font="'
                               +self.get_default_font_family_for_language(lc_messages_lang)
                               +' '+LABEL3_FONT+'"' + FALLPARAM
                               + label_lang_full_form + '</span>')

    def detect_language(self, text: str) -> str:
        '''
        detecting language by langdetect and
        any langugage is not there in my dictionary then
        it'll only return the 'en' by default
        '''
        text = text.strip()
        LOGGER.info('Trying to detect language of: %s', text)
        lang = 'en'
        if text:
            try:
                lang = langdetect.detect(text)
            except langdetect.LangDetectException as error:
                LOGGER.exception('Problem detecting language: %s: %s',
                                 error.__class__.__name__, error)
                lang = 'en'
        if '-' in lang:
            (first, rest) = lang.split('-', maxsplit=1)
            lang = first + '_' + rest.upper()
        return lang

    def get_default_font_family_for_language(self, lang: str) -> str:
        '''
        getting default font by fc-match
        '''
        lang = lang.replace('_','-')
        LOGGER.info('language: %s',lang)
        fc_match_binary = shutil.which('fc-match')
        if not fc_match_binary:
            return ''
        try:
            result = subprocess.run(
                    [fc_match_binary, f':lang={lang}', 'family', 'style', 'file'],
                    encoding='utf-8', check=True, capture_output=True,
                    env={'LC_ALL': lang.replace('-', '_')})
            pattern = re.compile(r'^(?P<families>.*):style=.*$')
            match = pattern.match(result.stdout.strip())
            if not match:
                LOGGER.error('Regexp did not match')
                return ''
            families = match.group('families').split(',')
            LOGGER.info('default font families=%s', families)
            if families:
                last_family = families[-1:][0]
                LOGGER.info('selected default font = %s',last_family)
                return last_family
            return ''
        except FileNotFoundError as error:
            LOGGER.exception('Exception when calling %s: %s: %s',
                             fc_match_binary, error.__class__.__name__, error)
            return ''
        except subprocess.CalledProcessError as error:
            LOGGER.exception('Exception when calling %s: %s: %s stderr: %s',
                             fc_match_binary,
                             error.__class__.__name__, error, error.stderr)
            return ''
        except Exception as error: # pylint: disable=broad-except
            LOGGER.exception('Exception when calling %s: %s: %s',
                             fc_match_binary, error.__class__.__name__, error)
            return ''

    #----------selecting random font for label2

    def get_random_font_family_for_language(self, lang: str) -> str:
        '''
        getting a random font using fc-list
        '''
        lang = lang.replace('_','-')
        fc_list_binary = shutil.which('fc-list')
        if not fc_list_binary:
            return ''
        try:
            result = subprocess.run(
                    [fc_list_binary, f':lang={lang}', 'family', 'style'],
                    encoding='utf-8', check=True, capture_output=True)
            fonts_listed = result.stdout.strip().split('\n')
            list_unfilter_random_font = [x for x in fonts_listed
                                         if not ('Droid' in x or 'STIX' in x)]
            random_font = random.choice(list_unfilter_random_font)
            LOGGER.info('selected random list from fc-list = %s',random_font)
            if random_font:
                #diable error label when font available
                self.label_error.hide()
            else:
                LOGGER.info('fonts are not installed for %s language',lang)
                #error level show no font installed
                label_error_text = "NOTE : fonts are not installed for " + lang + " language"
                #self.label_error.set_text(label_error_text)
                self.label_error.set_markup('<span foreground='+"'red'"+ 'font="'+self.get_default_font_family_for_language('en')
                         +' '+'10'+'"' + FALLPARAM
                         + '<b>' + label_error_text + '</b>'
                         + '</span>')
                self.label_error.show()
                return ''
            #sometimes random_font doesnot contain any style then error arises
            if random_font.find(":style") != -1:
                pattern = re.compile(r'^(?P<families>.*):style=(?P<style>.*)$')
            else:
                pattern = re.compile(r'^(?P<families>.*)$')
            match = pattern.match(random_font)
            if not match:
                LOGGER.error('Regexp did not match %s', result.stdout.strip())
                return ''
            families = match.group('families').split(',')
            LOGGER.info('Random font families=%s', families)
            last_family = ''
            if families:
                last_family = families[-1:][0]
                LOGGER.info('selected random font before confirm = %s',last_family)
            if not last_family:
                return ''
            LOGGER.info('selected random font confirm = %s',last_family)
            return last_family
        except FileNotFoundError as error:
            LOGGER.exception('Exception when calling %s: %s: %s',
                             fc_list_binary, error.__class__.__name__, error)
            return ''
        except subprocess.CalledProcessError as error:
            LOGGER.exception('Exception when calling %s: %s: %s stderr: %s',
                             fc_list_binary,
                             error.__class__.__name__, error, error.stderr)
            return ''
        except Exception as error: # pylint: disable=broad-except
            LOGGER.exception('Exception when calling %s: %s: %s',
                             fc_list_binary, error.__class__.__name__, error)
            return ''

def on_activate(application: Gtk.Application) -> None:
    '''
    activating the application by adding the application into gtk window
    '''
    win = AppWindow(application)
    win.present()

#langtable languages fro testing
def list_languages_langtable() -> List[str]:
    '''Return a list of languages known by langtable'''
    languages: List[str] = []
    for language_id in langtable._languages_db: # pylint: disable=protected-access
        # Parsing the language_id and reassembling is to remove the
        # script if there is one. For example if language_id is
        # “zh_Hant_TW” we remove the script “Hant” and leave just
        # “zh_TW”. We cannot really use the script part from a CLDR
        # style locale name because fontconfig does not use it.
        locale_object = langtable.parse_locale(language_id)
        if locale_object.territory:
            languages.append(
                locale_object.language + '_' + locale_object.territory)
        else:
            languages.append(locale_object.language)
    return languages

def list_languages_python() -> List[str]:
    '''Return a list of languages known by Python'''
    languages: List[str] = []
    for _alias, value in locale.locale_alias.items():
        value = value.split('.')[0]
        value = value.split('@')[0]
        exclude = (
            # AA is only a NATO code, not in ISO_3166-2
            'ar_AA',
            # https://en.wikipedia.org/wiki/Ewe_language an African
            # language, I think it has nothing to do with EE (Estonia)
            'ee_EE',
            'eo_XX', # XX Territory does not exist
            # “pd” is not an iso-639-1 code:
            # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
            # Probably it means “Pennsylvania Dutch”:
            # https://en.wikipedia.org/wiki/Pennsylvania_Dutch
            'pd',
            'pd_DE',
            'pd_US',
            # ph is not an iso-639-1 code. I guess “fil” was meant.
            'ph',
            'ph_PH',
            # pp is not an iso-639-1 code. I guess “pap” was meant.
            'pp',
            'pp_AN',
            'C', # POSIX locale, not really a language
        )
        if value in exclude:
            continue
        if value and value not in languages:
            languages.append(value)
        if '_' in value:
            lang_only = value.split('_')[0]
            if lang_only and lang_only not in languages:
                languages.append(lang_only)
    return languages

def list_languages_glibc() -> List[str]:
    '''
    Return a list of languages for the currently installed glibc locales
    '''
    languages: List[str] = []
    locale_binary = shutil.which('locale')
    if not locale_binary:
        return languages
    result_lines: List[str] = []
    try:
        result = subprocess.run(
                [locale_binary, '-a'],
                encoding='utf-8', check=True, capture_output=True)
    except FileNotFoundError as error:
        LOGGER.exception('Exception when calling %s: %s: %s',
                         locale_binary, error.__class__.__name__, error)
        return languages
    except subprocess.CalledProcessError as error:
        LOGGER.exception('Exception when calling %s: %s: %s stderr: %s',
                         locale_binary,
                         error.__class__.__name__, error, error.stderr)
        return languages
    except Exception as error: # pylint: disable=broad-except
        LOGGER.exception('Exception when calling %s: %s: %s',
                         locale_binary, error.__class__.__name__, error)
        return languages
    if not result:
        return languages
    result_lines = result.stdout.strip().split('\n')
    for line in result_lines:
        locale_object = langtable.parse_locale(line)
        lang = locale_object.language
        if not lang:
            continue
        if lang not in languages:
            languages.append(lang)
        if locale_object.territory:
            lang += '_' + locale_object.territory
        if lang not in languages:
            languages.append(lang)
    return languages

def list_languages_fontconfig() -> List[str]:
    '''
    Return a list of languages for which fonts are currently
    installed according to fontconfig
    '''
    languages: List[str] = []
    fc_list_binary = shutil.which('fc-list')
    if not fc_list_binary:
        return languages
    result_lines: List[str] = []
    try:
        result = subprocess.run(
                [fc_list_binary, ':', 'lang'],
                encoding='utf-8', check=True, capture_output=True)
    except FileNotFoundError as error:
        LOGGER.exception('Exception when calling %s: %s: %s',
                         fc_list_binary, error.__class__.__name__, error)
        return languages
    except subprocess.CalledProcessError as error:
        LOGGER.exception('Exception when calling %s: %s: %s stderr: %s',
                         fc_list_binary,
                         error.__class__.__name__, error, error.stderr)
        return languages
    except Exception as error: # pylint: disable=broad-except
        LOGGER.exception('Exception when calling %s: %s: %s',
                         fc_list_binary, error.__class__.__name__, error)
        return languages
    if not result:
        return languages
    result_lines = result.stdout.strip().split('\n')
    for line in result_lines:
        if not line.startswith(':lang='):
            continue
        for lang in line.replace(':lang=', '').split('|'):
            if lang in ('und-zmth', 'und-zsye'):
                # 'und-zmth' are mathematical symbols, 'und-zsye' are
                # emoji.  These are not “real” languages, better skip
                # them.
                continue
            if '-' in lang:
                (first, rest) = lang.split('-', maxsplit=1)
                lang = first + '_' + rest.upper()
            if lang and lang not in languages:
                languages.append(lang)
    return languages

def list_languages() -> List[str]:
    '''
    Return a list of languages combining the languages known by
    langtable, fontconfig, and glibc.
    '''
    languages: List[str] = []
    #languages: []
    #languages = list_languages_python()
    languages = list_languages_fontconfig()
    #for lang in list_languages_fontconfig():
    #    if lang not in languages:
    #        languages.append(lang)
    for lang in list_languages_glibc():
        if lang not in languages:
            languages.append(lang)
    #for lang in list_languages_python():
    #    if lang not in languages:
    #        languages.append(lang)
    for lang in list_languages_langtable():#jft
        if lang not in languages:
            languages.append(lang)
    return languages

def get_effective_lc_messages() -> str:
    '''Returns the effective value of LC_MESSAGES'''
    if 'LC_ALL' in os.environ:
        return os.environ['LC_ALL']
    if 'LC_MESSAGES' in os.environ:
        return os.environ['LC_MESSAGES']
    if 'LANG' in os.environ:
        return os.environ['LANG']
    return 'C'

def is_right_to_left_messages() -> bool:
    '''
    Check whether the effective LC_MESSAGES locale points to a languages
    which is usually written in a right-to-left script.

    :return: True if right-to-left, False if not.
    '''
    lc_messages_locale = get_effective_lc_messages()
    if not lc_messages_locale:
        return False
    lang = lc_messages_locale.split('_')[0]
    if lang in ('ar', 'arc', 'dv', 'fa', 'he', 'ps', 'syr', 'ur', 'yi'):
        # 'ku' could be Latin script or Arabic script or even Cyrillic
        # or Armenian script
        #
        # 'rhg' (Rohingya) could be written in Rohg (RTL),
        # Arab (RTL), Mymr (LTR), Latn (LTR), Beng (LTR)
        # There is no glibc locale yet for 'rhg'
        #
        # 'man' uses the Nkoo script (RTL)
        # Ther are several varieties of 'man': 'kao', 'mlq', 'mnk',
        # 'mwk', 'xkg', 'jad', 'rkm', 'bm', 'bam', 'mku', 'emk', 'msc'
        # 'mzj', 'jod', 'jud', 'kfo', 'kga', 'mxx', 'dyu', 'bof', 'skq'
        # There is no glibc locale yet for any of these.
        #
        # 'ff', (Fula) is written in Adlm (RTL). There is no glibc locale yet.
        return True
    return False

# Mapping of Unicode ordinals to Unicode ordinals, strings, or None.
# Unmapped characters are left untouched. Characters mapped to None
# are deleted.

# See also: https://www.icao.int/publications/Documents/9303_p3_cons_en.pdf
# Section 6, Page 30.

TRANS_TABLE = {
    ord('ẞ'): 'SS',
    ord('ß'): 'ss',
    ord('Ø'): 'O',
    ord('ø'): 'o',
    ord('Æ'): 'AE',
    ord('æ'): 'ae',
    ord('Œ'): 'OE',
    ord('œ'): 'oe',
    ord('Ł'): 'L',
    ord('ł'): 'l',
    ord('Þ'): 'TH',
    ord('Ħ'): 'H',
    ord('Ŋ'): 'N',
    ord('Ŧ'): 'T',
}

def remove_accents(text: str, keep: str = '') -> str:
    # pylint: disable=line-too-long
    '''Removes accents from the text

    Using “from unidecode import unidecode” is maybe more
    sophisticated, but I am not sure whether I can require
    “unidecode”. And maybe it cannot easily keep some accents for some
    languages.

    :param text: The text to change
    :param keep: A string of characters which should be kept unchanged
    :return: The text with some or all accents removed
             in NFC

    Examples:

    >>> remove_accents('Ångstrøm')
    'Angstrom'

    >>> remove_accents('ÅÆæŒœĳøßẞü')
    'AAEaeOEoeijossSSu'

    >>> remove_accents('abcÅøßẞüxyz')
    'abcAossSSuxyz'

    >>> unicodedata.normalize('NFC', remove_accents('abcÅøßẞüxyz', keep='åÅØø'))
    'abcÅøssSSuxyz'

    >>> unicodedata.normalize('NFC', remove_accents('alkoholförgiftning', keep='åÅÖö'))
    'alkoholförgiftning'

    '''
    # pylint: enable=line-too-long
    if not keep:
        result = ''.join([
            x for x in unicodedata.normalize('NFKD', text)
            if unicodedata.category(x) != 'Mn']).translate(TRANS_TABLE)
        return unicodedata.normalize('NFC', result)
    result = ''
    keep = unicodedata.normalize('NFC', keep)
    for char in unicodedata.normalize('NFC', text):
        if char in keep:
            result += char
            continue
        result += ''.join([
            x for x in unicodedata.normalize('NFKD', char)
            if unicodedata.category(x) != 'Mn']).translate(TRANS_TABLE)
    return unicodedata.normalize('NFC', result)

def locale_text_to_match(locale_id: str) -> str:
    '''
    Returns a text which can be matched against typed user input
    to check whether the user might be looking for this locale

    :param locale_id: The name of the locale

    Examples:

    >>> old_lc_all = os.environ.get('LC_ALL')
    >>> os.environ['LC_ALL'] = 'de_DE.UTF-8'

    >> locale_text_to_match('fr_FR')
    'fr_fr franzosisch (frankreich) francais (france) french (france)'

    >>> if old_lc_all:
    ...     os.environ['LC_ALL'] = old_lc_all
    ... else:
    ...     # unneeded return value assigned to variable
    ...     _ = os.environ.pop('LC_ALL', None)
    '''
    effective_lc_messages = get_effective_lc_messages()
    text_to_match = locale_id.replace(' ', '')
    query_languages = [effective_lc_messages, locale_id, 'en']
    for query_language in query_languages:
        if query_language:
            text_to_match += ' ' + langtable.language_name(
                languageId=locale_id,
                languageIdQuery=query_language)
    return remove_accents(text_to_match).lower()

def locale_language_description(locale_id: str) -> str:
    '''
    Returns a description of the language of the locale

    :param locale_id: The name of the locale

    Examples:

    >>> old_lc_all = os.environ.get('LC_ALL')
    >>> os.environ['LC_ALL'] = 'de_DE_IN.UTF-8'

    >> locale_language_description('fr_FR')
    'Französisch (Frankreich)'

    >>> if old_lc_all:
    ...     os.environ['LC_ALL'] = old_lc_all
    ... else:
    ...     # unneeded return value assigned to variable
    ...     _ = os.environ.pop('LC_ALL', None)
    '''
    language_description = ''
    effective_lc_messages = get_effective_lc_messages()
    language_description = langtable.language_name(
        languageId=locale_id,
        languageIdQuery=effective_lc_messages)
    if not language_description:
        language_description = langtable.language_name(
            languageId=locale_id, languageIdQuery='en')
    if language_description:
        language_description = (
            language_description[0].upper() + language_description[1:])
    return language_description

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    if _ARGS.debug:
        LOG_HANDLER = logging.StreamHandler(stream=sys.stderr)
        LOG_FORMATTER = logging.Formatter(
                '%(asctime)s %(filename)s '
                'line %(lineno)d %(funcName)s %(levelname)s: '
                '%(message)s')
        LOG_HANDLER.setFormatter(LOG_FORMATTER)
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.addHandler(LOG_HANDLER)
    else:
        LOG_HANDLER_NULL = logging.NullHandler()
    #getting width, height of entire screen
    #width = Gtk.screen_width()
    #print('width of screen ',width)
    #print('height of screen ',height)
    list_dropdown = sorted(list_languages())
    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)
