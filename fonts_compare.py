#!/usr/bin/python3
'''
This is my fonts-compare program for font rendering and comparing
'''
from typing import Any
import sys
import random
import re
import subprocess
import shutil
import locale
import argparse
import logging
import langtable # type: ignore
import langdetect # type: ignore
import gi # type: ignore
# pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk # type: ignore
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

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.props.halign = Gtk.Align.CENTER
        self.vbox.set_margin_top(25)

        self.vbox_last = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox_last.set_margin_top(20)
        self.vbox_last.set_margin_bottom(20)
        self.vbox_last.props.halign = Gtk.Align.CENTER

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

        self.entry = Gtk.Entry()
        self.entry.connect('notify::text', self.on_entry_changed)
        self.label3 = Gtk.Label(label="")
        self.vbox.append(self.entry)
        self.vbox.append(self.label3)

        self.combo = Gtk.ComboBoxText()
        self.label4 = Gtk.Label()
        self.label4.set_markup('<span font="'+get_default_font_family_for_language('en')
                +' '+'15'+'"' + FALLPARAM
                + 'Select Language'
                + '</span>')
        self.hbox3.append(self.label4)
        self.hbox3.append(self.combo)
        self.vbox.append(self.hbox3)

        #switch button/toggle button - pango or langtable sample string
        self.label5 = Gtk.Label()
        self.label5.set_markup('<span font="'+get_default_font_family_for_language('en')
                +' '+'15'+'"' + FALLPARAM
                + ' Use Sample Text :  '
                + '</span>')
        self.hbox4.append(self.label5)
        self.label_switch_prev = Gtk.Label(label = 'Pango')
        self.label_switch_next = Gtk.Label(label = 'LangTable')
        self.switch = Gtk.Switch()
        self.switch.set_active(False)
        self.switch.connect("state-set", self.switch_switched)
        self.hbox4.append(self.label_switch_prev)
        self.hbox4.append(self.switch)
        self.hbox4.append(self.label_switch_next)
        self.vbox.append(self.hbox4)

        self.label1 = Gtk.Label()
        self.button1 = Gtk.FontButton.new()
        self.fontbutton(self.label1, self.button1, self.hbox1)
        self.vbox.append(self.hbox1)
        self.vbox.append(self.label1)
        self.label2 = Gtk.Label()
        self.button2 = Gtk.FontButton.new()
        self.fontbutton(self.label2, self.button2, self.vbox_last)
        self.vbox.append(self.label2)
        self.vbox.append(self.vbox_last)
        temp_random_font = get_random_font_family_for_language('en')
        self.label2.set_markup('<span font="'+temp_random_font
                +' '+FONTSIZE+'"' + FALLPARAM
                + sample_text_selector('en')
                + '</span>')
        self.button2.set_font(temp_random_font + ' ' + FONTSIZE)

        #wrap
        self.label1.set_wrap(True)
        self.label2.set_wrap(True)

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
        self.label_slider = Gtk.Label()
        self.label_slider.set_markup('<span font="'+get_default_font_family_for_language('en')
                +' '+'15'+'"' + FALLPARAM
                + 'Select FontSize'
                + '</span>')
        self.vbox_last.append(self.label_slider)
        self.vbox_last.append(self.slider)

        list_dropdown.sort()
        for lang in list_dropdown:
            self.combo.append_text(lang)
        # Make 'en' active by default to avoid seeing an empty
        # assume that and just search for 'en' whereever it is):
        for i, item in enumerate(self.combo.get_model()):
            if item[0] == 'en':
                self.combo.set_active(i)
        self.combo.changed_signal_id = self.combo.connect('changed', self.on_changed)


        text = self.label1.get_text()
        lang = detect_language(text)
        LOGGER.info('label1: text=%s lang=%s', text,lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup(
                f'<span font="{get_default_font_family_for_language(lc_messages_lang)} '
                f'{LABEL3_FONT}" {FALLPARAM}{label_lang_full_form}</span>')

        #self.set_default_size(450, 450)
        self.set_resizable(False)
        self.set_child(self.vbox)
        #scrolled = Gtk.ScrolledWindow()
        #scrolled.set_child(self.vbox)
        #self.set_child(scrolled)

    def fontbutton(
            self,
            label: Gtk.Label,
            button: Gtk.FontButton,
            boxh: Gtk.Box) -> None:
        '''
        setting up initial font and text for labels and font button text updated
        '''
        temp_label_button_font = get_default_font_family_for_language('en')
        label.set_markup('<span font="'+temp_label_button_font
                +' '+FONTSIZE+'"' + FALLPARAM
                + sample_text_selector('en')
                + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(temp_label_button_font + ' ' + FONTSIZE)
        boxh.append(button)
        #self.vbox.append(boxh)
        #self.vbox.append(label)

    def switch_switched(
            self,
            switch: Gtk.Switch,
            state):
        '''
        function to change sample string depends upon toogle switch
        '''
        print(f"The switch has been switched {'on' if state else 'off'}")
        print('switch_switched state : ',state)
        global STATE_UNIV
        if state:
            #self.set_title('switch button is clicked')
            #sample_text by langtable.language_name
            #global STATE_UNIV
            STATE_UNIV = state
        else:
            #self.set_title('switch button is NOT clicked')
            #sample_text by Pango.Language
            #global STATE_UNIV
            STATE_UNIV = state
        #instant lab1l and label2 change after switch change
        #self.set_font(self.combo.get_active_text(),
        #    sample_text_selector(self.combo.get_active_text()))
        self.label1.set_markup('<span font="'+self.button1.get_font()+'"' + FALLPARAM
                + sample_text_selector(self.combo.get_active_text())
                + '</span>')
        self.label2.set_markup('<span font="'+self.button2.get_font()+'"' + FALLPARAM
                + sample_text_selector(self.combo.get_active_text())
                + '</span>')

    def slider_changed(
            self,
            slider: Gtk.Scale,
            button1_family: str,
            button2_family: str) -> None:
        '''Called when the slider is moved'''
        #both text labels will change it's fontsize depending upon font's slider

        button1_family = self.button1.get_font().rsplit(' ',1)[0]
        button2_family = self.button2.get_font().rsplit(' ',1)[0]
        self.button1.set_font(button1_family + ' ' + str(int(slider.get_value())))
        self.button2.set_font(button2_family + ' ' + str(int(slider.get_value())))
        self.label1.set_markup('<span font="'+self.button1.get_font()+'"' + FALLPARAM
                + self.label1.get_text()
                + '</span>')
        self.label2.set_markup('<span font="'+self.button2.get_font()+'"' + FALLPARAM
                + self.label2.get_text()
                + '</span>')

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
        temp_label1_font = get_default_font_family_for_language(detect_lang)
        self.label1.set_markup('<span font="'+temp_label1_font
                +' '+str(int(self.slider.get_value()))+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button1.set_font(%s)',
                temp_label1_font +' '+str(int(self.slider.get_value())))
        self.button1.set_font(temp_label1_font +' '+str(int(self.slider.get_value())))
        LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
        temp_label2_font = get_random_font_family_for_language(detect_lang)
        self.label2.set_markup('<span font="'+temp_label2_font
                +' '+str(int(self.slider.get_value()))+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button2.set_font(%s)',
                temp_label2_font +' '+ str(int(self.slider.get_value())))
        self.button2.set_font(temp_label2_font +' '+ str(int(self.slider.get_value())))
        LOGGER.info('self.button2.get_font(%s)',self.button2.get_font())

    def on_entry_changed(self, widget: Gtk.Entry, _property_spec: Any) -> None:
        '''Called when the text in the entry has changed.

        While typing on gtk entry box, the language is detected
        automatically time and then the font family and fontsize to
        display the text on label3 is changed accordingly.
        '''
        text = widget.get_text()
        lang = detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        LOGGER.info('label_lang full form=%s',label_lang_full_form)
        self.label3.set_markup('<span font="'+get_default_font_family_for_language(lc_messages_lang)
                +' '+LABEL3_FONT+'"' + FALLPARAM
                + label_lang_full_form + '</span>')
        if lang in list_dropdown:
            self.button1.set_preview_text(langtable.language_name(
                languageId=lang, languageIdQuery=lang))
            self.button2.set_preview_text(langtable.language_name(
                languageId=lang, languageIdQuery=lang))
            self.set_font(lang, text)
            self.combo.handler_block(self.combo.changed_signal_id)
            for i, item in enumerate(self.combo.get_model()):
                if item[0] == lang:
                    self.combo.set_active(i)
            self.combo.handler_unblock(self.combo.changed_signal_id)
        elif not lang in list_dropdown:
            LOGGER.info('%s is not there in dropdown list',label_lang_full_form)
            self.label1.set_markup('<span font="'
                    +get_default_font_family_for_language(lang)
                    +' '+FONTSIZE+'"' + FALLPARAM
                    + text + '</span>')
            LOGGER.info('self.button1.set_font(%s)',
                    get_default_font_family_for_language(lang)
                    +' '+FONTSIZE)
            self.button1.set_font(
                    get_default_font_family_for_language(lang)
                    +' '+FONTSIZE)
            LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
            self.label2.set_markup('<span font="'
                    +get_default_font_family_for_language(lang)
                    +' '+FONTSIZE+'"' + FALLPARAM
                    + text + '</span>')
            LOGGER.info('self.button2.set_font(%s)',
                    get_default_font_family_for_language(lang)
                    +' '+ FONTSIZE)
            self.button2.set_font(
                    get_default_font_family_for_language(lang)
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
        #text = langtable.language_name(languageId=lang, languageIdQuery=lang)
        text = sample_text_selector(lang)
        self.entry.set_text(text)
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
                lc_messages_lang, get_default_font_family_for_language(lc_messages_lang))
        self.label3.set_markup('<span font="'+get_default_font_family_for_language(lc_messages_lang)
                +' '+LABEL3_FONT+'"' + FALLPARAM
                + label_lang_full_form + '</span>')

def detect_language(text: str) -> str:
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

def on_activate(application: Gtk.Application) -> None:
    '''
    activating the application by adding the application into gtk window
    '''
    win = AppWindow(application)
    win.present()

def get_default_font_family_for_language(lang: str) -> str:
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
                encoding='utf-8', check=True, capture_output=True)
        pattern = re.compile(r'^(?P<families>.*):style=.*$')
        match = pattern.match(result.stdout.strip())
        if not match:
            LOGGER.error('Regexp did not match')
            return ''
        families = match.group('families').split(',')
        LOGGER.info('default font families=%s', families)
        if families:
            last_family = families[-1:][0]
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

def get_random_font_family_for_language(lang: str) -> str:
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
        pattern = re.compile(r'^(?P<families>.*):style=(?P<style>.*)$')
        match = pattern.match(random_font)
        if not match:
            LOGGER.error('Regexp did not match %s', result.stdout.strip())
            return ''
        families = match.group('families').split(',')
        LOGGER.info('Random font families=%s', families)
        last_family = ''
        if families:
            last_family = families[-1:][0]
        if not last_family:
            return ''
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


def sample_text_selector(lang: str) -> str:
    '''
    sample text will be selected by either Pango or Langtable
    '''
    print('sample_text_selector STATE_UNIV : ',STATE_UNIV)
    if STATE_UNIV:
        #True - Langtable sample text
        sample_text = langtable.language_name(languageId=lang, languageIdQuery=lang)
        return sample_text
    #else - False - Pango sample text
    sample_text = Pango.Language.get_sample_string(Pango.language_from_string (lang))
    return sample_text



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

    STATE_UNIV = False
    list_dropdown = ['en','bn','ja','hi','mr','ta','ko','de','da','gu','ar','zh_CN']
    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)
