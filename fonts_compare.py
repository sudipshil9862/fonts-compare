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
import langtable
import langdetect
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
#gi.require_version('Gio', '2.0')
#from gi.repository import Gio
gi.require_version('Pango', '1.0')
from gi.repository import Pango

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
dic = {
        'en':{
            'text':'How are you'},
        'bn':{
            'text':'আপনি কেমন আছেন'},
        'ja':{
            'text':'元気ですか'},
        'hi':{
            'text':'आप कैसे हैं'},
        'mr':{
            'text':'तू कसा आहेस'},
        'ta':{
            'text':'நீங்கள் எப்படி இருக்கிறீர்கள்'},
        'ko':{
            'text':'어떻게 지내세요'},
        'de':{
            'text':'wie gehts'},
        'da':{
            'text':'Hvordan har du det'},
        'gu':{
            'text':'તમે કેમ છો'},
        'ar':{
            'text':'كيف حالك؟'}

        }

class AppWindow(Gtk.ApplicationWindow):
    '''
    Including appwindow class to window to present
    '''
    def __init__(self, appp):
        super().__init__(application=appp)
        self.init_ui()

    def init_ui(self):
        '''
        init_ui contains all the containers, labels, buttons
        '''
        self.set_title('Font Compare')

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox.props.halign = Gtk.Align.CENTER
        self.vbox4 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.hbox1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox1.set_margin_top(10)

        self.hbox2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox2.set_margin_top(10)

        self.hbox3 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox3.set_margin_top(5)
        self.hbox3.props.halign = Gtk.Align.CENTER

        self.vbox5 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.vbox5.set_margin_top(5)
        self.vbox5.set_margin_start(50)
        self.vbox5.set_margin_end(50)
        self.vbox5.props.halign = Gtk.Align.CENTER
        
        self.hbox5 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox5.set_margin_top(5)
        self.hbox5.props.halign = Gtk.Align.CENTER

        self.vbox.set_margin_start(20)
        self.vbox.set_margin_top(25)
        self.vbox.set_margin_end(20)

        self.vbox4.set_margin_top(20)
        self.vbox4.set_margin_bottom(20)

        self.entry = Gtk.Entry()
        self.label3 = Gtk.Label(label="")
        self.vbox.append(self.entry)
        self.vbox.append(self.label3)


        self.combo = Gtk.ComboBoxText()
        self.label4 = Gtk.Label()
        self.label4.set_markup('<span font="'+dic['en']['family']
                +' '+'15'+'"' + FALLPARAM
                + 'Select Language'
                + '</span>')
        self.hbox3.append(self.label4)
        self.hbox3.append(self.combo)
        self.vbox.append(self.hbox3)

        self.label1 = Gtk.Label()
        self.button1 = Gtk.FontButton.new()
        self.fontbutton(self.label1, self.button1, self.hbox1)
        self.label2 = Gtk.Label()
        self.button2 = Gtk.FontButton.new()
        self.fontbutton(self.label2, self.button2, self.hbox2)
        self.label2.set_markup('<span font="'+dic['en']['family2']
                +' '+FONTSIZE+'"' + FALLPARAM
                + 'Fonts Compare'
                + '</span>')
        self.button2.set_font(dic['en']['family2'] + ' ' + FONTSIZE)


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
        self.label_slider.set_markup('<span font="'+dic['en']['family']
                +' '+'15'+'"' + FALLPARAM
                + 'Select FontSize'
                + '</span>')
        self.vbox4.append(self.label_slider)
        self.vbox4.append(self.slider)
        self.vbox.append(self.vbox4)
        self.vbox.append(self.vbox5)


        for lang in sorted(dic, key = lambda x: (
            x != 'en', # Put 'en' on top
            x, # Sort everything else alphabetically
            )):
            self.combo.append_text(lang)
        # Make 'en' active by default to avoid seeing an empty
        # combobox at program start (We know that 'en' is at index 0
        # because of the way we sorted above, but let’s better not
        # assume that and just search for 'en' whereever it is):
        for i, item in enumerate(self.combo.get_model()):
            if item[0] == 'en':
                self.combo.set_active(i)
        self.combo.changed_signal_id = self.combo.connect('changed', self.on_changed)


        text = self.label1.get_text()
        lang = detect_language(text)
        LOGGER.info('label1: text=%s lang=%s', text,lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup(
                f'<span font="{dic[lc_messages_lang]["family"]} '
                f'{LABEL3_FONT}" {FALLPARAM}{label_lang_full_form}</span>')

        keycont = Gtk.EventControllerKey()
        keycont.connect('key-released', self.on_key_released)
        self.add_controller(keycont)
        width = 1
        height = 1
        #self.set_default_size(450, 450)
        self.set_resizable(True);
        self.set_child(self.vbox)

   
    def fontbutton(self, label, button, boxh):
        '''
        setting up initial font and text for labels and font button text updated
        '''
        label.set_markup('<span font="'+dic['en']['family']
                +' '+FONTSIZE+'"' + FALLPARAM
                + 'Fonts Compare'
                + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(dic['en']['family'] + ' ' + FONTSIZE)
        boxh.append(button)
        self.vbox.append(boxh)
        self.vbox.append(label)

    def slider_changed(self, slider, button1_family, button2_family):
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
                +' '+str(int(self.slider.get_value()))+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button1.set_font(%s)',
                dic[detect_lang]['family'] +' '+str(int(self.slider.get_value())))
        self.button1.set_font(dic[detect_lang]['family'] +' '+str(int(self.slider.get_value())))
        LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
        self.label2.set_markup('<span font="'+dic[detect_lang]['family2']
                +' '+str(int(self.slider.get_value()))+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button2.set_font(%s)',
                dic[detect_lang]['family2'] +' '+ str(int(self.slider.get_value())))
        self.button2.set_font(dic[detect_lang]['family2'] +' '+ str(int(self.slider.get_value())))
        LOGGER.info('self.button2.get_font(%s)',self.button2.get_font())

    def on_key_released(self, *_):
        '''
        while typing on gtk entry box..
        the langugage is detected automatically with same time and also
        setting up label3 text's font family and fontsize
        '''
        text = self.entry.get_text()
        lang = detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']
                +' '+LABEL3_FONT+'"' + FALLPARAM
                + label_lang_full_form + '</span>')
        if lang in dic:
            self.button1.set_preview_text(dic[lang]['text'])
            self.button2.set_preview_text(dic[lang]['text'])
            self.set_font(lang, text)
            self.combo.handler_block(self.combo.changed_signal_id)
            for i, item in enumerate(self.combo.get_model()):
                if item[0] == lang:
                    self.combo.set_active(i)
            self.combo.handler_unblock(self.combo.changed_signal_id)
        elif not lang in dic:
            LOGGER.info('%s is not there in dic',label_lang_full_form)
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

    def on_changed(self, wid):
        '''
        when we select a perticular langugage from the drop-down..
        if it's bengali then take one bengali text,
        setting up bengali fonts on set_font function,
        display the language full form in label3 depends upon
        which is the default langugage for the user have
        '''
        lang = wid.get_active_text()
        LOGGER.info('%s is selected from drop-down',lang)
        text = dic[lang]['text']
        self.entry.set_text(text)
        #set_preview_text means -
        #Setting the sample text for specific selected language
        #into the sample text field section at the bottom of the Gtk font selection dialog
        self.button1.set_preview_text(text)
        self.button2.set_preview_text(text)
        self.set_font(lang, text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang,
                languageIdQuery=lc_messages)
        LOGGER.debug('label_lang_full_form=%s', label_lang_full_form)
        LOGGER.debug('label3 local lang=%s, label3 font - dic[lc_messages_lang]["family"]=%s',
                lc_messages_lang, dic[lc_messages_lang]['family'])
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']
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
#font_filter() - filtering out and removing the fonts starts with 'Droid', 'STIX'
def font_filter(x):
    if x.find('Droid') != -1:
        return False
    elif x.find('STIX') != -1:
        return False
    elif x=='':
        return False
    elif x==' ':
        return False
    return True


def get_random_font_family_for_language(lang: str) -> str:
    '''
    getting a random font using fc-list
    '''
    fc_list_binary = shutil.which('fc-list')
    if not fc_list_binary:
        return ''
    try:
        result = subprocess.run(
                [fc_list_binary, f':lang={lang}', 'family', 'style'],
                encoding='utf-8', check=True, capture_output=True)
        fonts_listed = result.stdout.strip().split('\n')
        unfilter_random_font = filter(font_filter, fonts_listed)
        list_unfilter_random_font = list(unfilter_random_font)
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
        family2 = get_random_font_family_for_language(language)
        LOGGER.info('lang=%s random family=%s', language, family2)
        value['family2'] = family2

    LOGGER.info('dic=%s', dic)
    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)
