#!/usr/bin/python3
'''
This is my fonts-compare program for font rendering and comparing
'''
from typing import Any
import sys
import re
import subprocess
import shutil
import locale
import argparse
import logging
import langtable
import langdetect
import gi
from gi.repository import Gtk, Pango
gi.require_version('Gtk', '4.0')

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

#FONTWEIGHT = 'Regular'
#FALLPARAM = 'fallback="false">'
#FONTSIZE = '30'
FONTWEIGHT = 'Regular'
FALLPARAM = 'fallback="false">'
FONTSIZE = '30'
dic = {
    'en':{
		'text':'How are you'},
	'bn':{
		'text':'আপনি কেমন আছেন'},
	'ja':{
		'text':'元気ですか'},
	'ko':{
        'text':'어떻게 지내세요'},
	'de':{
		'text':'wie gehts'}
	}

class AppWindow(Gtk.ApplicationWindow):
    '''
    Including appwindow class to window to present
    '''
    def __init__(self, appp):
        #super(AppWindow, self).__init__(application=appp) #python2 style
        super().__init__(application=appp) #python 3
        self.init_ui()

    def init_ui(self):
        '''
        init_ui contains all the containers, labels, buttons
        '''
        self.set_title('Font Compare')

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox1 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox2 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox3 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox4 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.hbox1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox1.set_margin_top(10)

        self.hbox2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox2.set_margin_top(10)

        self.hbox3 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox3.set_margin_top(5)

        self.vbox.set_margin_start(150)
        self.vbox.set_margin_top(50)
        self.vbox.set_margin_end(150)

        self.vbox1.set_margin_top(20)
        self.vbox1.set_margin_bottom(20)
        self.vbox2.set_margin_top(20)
        self.vbox2.set_margin_bottom(20)
        self.vbox3.set_margin_top(20)
        self.vbox3.set_margin_bottom(20)

        self.label1 = Gtk.Label()
        self.button1 = Gtk.FontButton.new()
        self.fontbutton(self.label1, self.button1, self.hbox1, self.vbox1)
        self.label2 = Gtk.Label()
        self.button2 = Gtk.FontButton.new()
        self.fontbutton(self.label2, self.button2, self.hbox2, self.vbox2)

        self.entry = Gtk.Entry()
        self.label3 = Gtk.Label(label="")
        self.vbox3.append(self.entry)
        self.vbox3.append(self.label3)
        self.vbox.append(self.vbox3)

        self.combo = Gtk.ComboBoxText()
        self.hbox3.append(self.combo)
        self.vbox3.append(self.hbox3)
        self.vbox.append(self.vbox3)
        self.combo.append_text('en')#en
        self.combo.append_text('bn')#bn
        self.combo.append_text('ja')#ja
        self.combo.append_text('ko')#ko
        self.combo.append_text('de')#de
        # make 'en' active by default to avoid seeing an empty
        # combobox at program start:
        self.combo.set_active(0)
        self.combo.connect('changed', self.on_changed)

        text = self.label1.get_text()
        lang = detect_language(text)
        LOGGER.info('label1: text=%s lang=%s', text,lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
            languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup(
            f'<span font="{dic[lc_messages_lang]["family"]} '
            f'{FONTWEIGHT} {FONTSIZE}" {FALLPARAM}{label_lang_full_form}</span>')

        keycont = Gtk.EventControllerKey()
        keycont.connect('key-released', self.on_key_released)
        self.add_controller(keycont)

        self.set_default_size(450, 450)
        self.set_child(self.vbox)

    def fontbutton(self, label, button, boxh, boxv):
        '''
        setting up initial font and text for labels and font button text updated
        '''
        label.set_markup('<span font="'+dic['en']['family']
                +' '+FONTWEIGHT+' '+FONTSIZE+'"' + FALLPARAM
                + 'Work Hard and achieve anything'
                + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(dic['en']['family'] + ' ' + FONTWEIGHT +' '+ FONTSIZE)
        boxh.append(button)
        boxv.append(boxh)
        boxv.append(label)
        self.vbox.append(boxv)

    @classmethod
    def label_font_change(cls, button, label):
        '''
        font family and font size changes by font-button dialog
        '''
        pango_font_description = Pango.FontDescription.from_string(str=button.get_font(),)
        pango_attr_font_desc = Pango.AttrFontDesc.new(desc=pango_font_description,)
        pango_attr_list = Pango.AttrList.new()
        pango_attr_list.insert(attr=pango_attr_font_desc)
        label.set_attributes(attrs=pango_attr_list)

    def set_font(self, detect_lang, set_text):
        '''
        setting up text,
        font family depending upon which language has detected
        '''
        self.label1.set_markup('<span font="'+dic[detect_lang]['family']
                +' '+FONTWEIGHT+' '+FONTSIZE+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button1.set_font(%s)',
                    dic[detect_lang]['family'] +' '+ FONTWEIGHT+' '+FONTSIZE)
        self.button1.set_font(dic[detect_lang]['family'] +' '+ FONTWEIGHT+' '+FONTSIZE)
        self.label2.set_markup('<span font="'+dic[detect_lang]['family']
                +' '+FONTWEIGHT+' '+FONTSIZE+'"' + FALLPARAM
                + set_text + '</span>')
        self.button2.set_font(dic[detect_lang]['family'] +' '+ FONTWEIGHT+' '+FONTSIZE)

    def on_key_released(self, *_):
        '''
        while typing on gtk entry box..
        the langugage is detected automatically with same time and also
        setting up label3 text's font family and fontsize
        '''
        text = self.entry.get_text()
        lang = detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        self.button1.set_preview_text(dic[lang]['text'])
        self.button2.set_preview_text(dic[lang]['text'])
        self.set_font(lang, text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
            languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']
                +' '+FONTWEIGHT+' '+FONTSIZE+'"' + FALLPARAM
                + label_lang_full_form + '</span>') 
        if lang == 'en': self.combo.set_active(0)
        elif lang == 'bn': self.combo.set_active(1)
        elif lang == 'ja': self.combo.set_active(2)
        elif lang == 'ko': self.combo.set_active(3)
        elif lang == 'de': self.combo.set_active(4)


    def on_changed(self, wid):
        '''
        when we select a perticular langugage from the drop-down..
        if it's bengali then take one bengali text,
        setting up bengali fonts on set_font function,
        display the language full form in label3 depends upon
        which is the default langugage for the user have
        '''
        LOGGER.info('on_changed started...')
        lang = wid.get_active_text()
        text = dic[lang]['text']
        self.entry.set_text(text)
        self.button1.set_preview_text(text)
        self.button2.set_preview_text(text)
        self.set_font(lang, text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
            languageId=lang,
            languageIdQuery=lc_messages)
        LOGGER.debug('lc_messages_lang=%s label_lang_full_form=%s',
                    lc_messages_lang, label_lang_full_form)
        LOGGER.debug('dic[lc_messages_lang]["family"]=%s',
                     dic[lc_messages_lang]['family'])
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']
                +' '+FONTWEIGHT+' '+FONTSIZE+'"' + FALLPARAM
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
    if not lang in dic:
        LOGGER.error(
            'lang=%s was detected but we don’t have that in dic'
            'falling back to "en".',
            lang)
        lang = 'en'
    return lang

def on_activate(application):
    '''
    activating the application by adding the application into gtk window
    '''
    win = AppWindow(application)
    win.present()

def get_default_font_family_for_language(lang: str) -> str:
    '''
    getting default font by fc-match
    '''
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
        LOGGER.info('families=%s', families)
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
    for language, value in dic.items():
        family = get_default_font_family_for_language(language)
        LOGGER.info('lang=%s default family=%s', language, family)
        value['family'] = family
    LOGGER.info('dic=%s', dic)
    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)
