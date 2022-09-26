#!/usr/bin/python3

from typing import Any
import sys
import re
import subprocess
import shutil
import logging
import langtable
import locale
import argparse
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango
import langdetect

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

fontweight = 'Regular'
fallParam = 'fallback="false">'
fontsize = '30'
dic = {'en':{
        'family':'Noto Sans',
		'text':'How are you'},
	'bn':{
        'family':'Noto Sans Bengali',
		'text':'আপনি কেমন আছেন'},
	'ja':{
        'family':'Noto Sans CJK JP',
		'text':'元気ですか'},
	'ko':{
        'family':'Noto Sans CJK KR',
        'text':'어떻게 지내세요'},
	'de':{
        'family':'Noto Sans',
		'text':'wie gehts'}
	}

class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, app):

        super(AppWindow, self).__init__(application=app)

        self.init_ui()

    def init_ui(self):

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

        combo = Gtk.ComboBoxText()
        self.hbox3.append(combo)
        self.vbox3.append(self.hbox3)
        self.vbox.append(self.vbox3)
        combo.connect('changed', self.on_changed)
        combo.append_text('en')#en
        combo.append_text('bn')#bn
        combo.append_text('ja')#ja
        combo.append_text('ko')#ko
        combo.append_text('de')#de
        # make 'en' active by default to avoid seeing an empty
        # combobox at program start:
        combo.set_active(0)

        text = self.label1.get_text()
        lang = detect_language(text)
        LOGGER.info('label1: text=%s lang=%s', text,lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label3DetectLang = langtable.language_name(
            languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup(
            f'<span font="{dic[lc_messages_lang]["family"]} '
            f'{fontweight} {fontsize}" {fallParam}{label3DetectLang}</span>')

        keycont = Gtk.EventControllerKey()
        keycont.connect('key-released', self.on_key_released)
        self.add_controller(keycont)

        self.set_default_size(450, 450)
        self.set_child(self.vbox)

    def fontbutton(self, label, button, boxh, boxv):
        label.set_markup('<span font="'+dic['en']['family']+' '+fontweight+' '+fontsize+'"' + fallParam + 'With hard work and effort, you can achieve anything' + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(dic['en']['family'] + ' ' + fontweight +' '+ fontsize)
        boxh.append(button)
        boxv.append(boxh)
        boxv.append(label)
        self.vbox.append(boxv)

    def label_font_change(self, button, label):
        pango_font_description = Pango.FontDescription.from_string(str=button.get_font(),)
        pango_attr_font_desc = Pango.AttrFontDesc.new(desc=pango_font_description,)
        pango_attr_list = Pango.AttrList.new()
        pango_attr_list.insert(attr=pango_attr_font_desc)
        label.set_attributes(attrs=pango_attr_list)

    def setFont(self, detectLang, setText):
        self.label1.set_markup('<span font="'+dic[detectLang]['family']+' '+fontweight+' '+fontsize+'"' + fallParam + setText + '</span>')
        LOGGER.info('self.button1.set_font(%s)',
                    dic[detectLang]['family'] +' '+ fontweight+' '+fontsize)
        self.button1.set_font(dic[detectLang]['family'] +' '+ fontweight+' '+fontsize)
        self.label2.set_markup('<span font="'+dic[detectLang]['family']+' '+fontweight+' '+fontsize+'"' + fallParam + setText + '</span>')
        self.button2.set_font(dic[detectLang]['family'] +' '+ fontweight+' '+fontsize)

    def on_key_released(self, *_):
        text = self.entry.get_text()
        lang = detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        self.setFont(lang, text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label3DetectLang = langtable.language_name(
            languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']+' '+fontweight+' '+fontsize+'"' + fallParam + label3DetectLang + '</span>')

    def on_changed(self, wid):
        lang = wid.get_active_text()
        self.setFont(lang, dic[lang]['text'])
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label3DetectLang = langtable.language_name(
            languageId=lang,
            languageIdQuery=lc_messages)
        LOGGER.debug('lc_messages_lang=%s label3DetectLang=%s',
                    lc_messages_lang, label3DetectLang)
        LOGGER.debug('dic[lc_messages_lang]["family"]=%s',
                     dic[lc_messages_lang]['family'])
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']+' '+fontweight+' '+fontsize+'"' + fallParam + label3DetectLang + '</span>')

def detect_language(text: str) -> str:
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

def on_activate(app):

    win = AppWindow(app)
    win.present()

def get_default_font_family_for_language(lang: str) -> str:
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
    except Exception as error:
        LOGGER.exception('Exception when calling %s: %s: %s',
                         fc_match_binary, error.__class__.__name__, error)
        return ''

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    if _ARGS.debug:
        LOG_HANDLER = logging.StreamHandler(stream=sys.stderr)
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.addHandler(LOG_HANDLER)
    else:
        LOG_HANDLER_NULL = logging.NullHandler()
    for lang in dic:
        family = get_default_font_family_for_language(lang)
        LOGGER.info('lang=%s default family=%s', lang, family)
        dic[lang]['family'] = family
    LOGGER.info('dic=%s', dic)
    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)
