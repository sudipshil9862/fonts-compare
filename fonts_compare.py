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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Pango
import fontconfig

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
FALLPARAM = 'fallback="false">'
FONTSIZE = '50'
label3_font = '20'
#DIALOG_WARNING = ''
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


#Custom Box class for dialog box
'''
class CustomDialog(Gtk.Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.parent = kwargs.get('transient_for')

        LOGGER.info('DIALOG_WARNING = %s',DIALOG_WARNING)
        self.set_title(title='Please Attention')
        self.use_header_bar = True
        #self.lang_dialog = lang_full_form
        self.connect('response', self.dialog_response)

        self.set_width = 683
        self.set_height = 384

        self.add_buttons(
            '_Cancel', Gtk.ResponseType.CANCEL,
            '_OK', Gtk.ResponseType.OK,
        )

        btn_ok = self.get_widget_for_response(
            response_id=Gtk.ResponseType.OK,
        )
        btn_ok.get_style_context().add_class(class_name='suggested-action')
        btn_cancel = self.get_widget_for_response(
            response_id=Gtk.ResponseType.CANCEL,
        )
        btn_cancel.get_style_context().add_class(class_name='destructive-action')

        content_area = self.get_content_area()
        content_area.set_orientation(orientation=Gtk.Orientation.VERTICAL)
        content_area.set_spacing(spacing=24)
        content_area.set_margin_top(margin=12)
        content_area.set_margin_end(margin=12)
        content_area.set_margin_bottom(margin=12)
        content_area.set_margin_start(margin=12)

        str_label = 'Fonts not installed for ' + DIALOG_WARNING + ' language'
        LOGGER.info('str_label = %s',str_label)
        LOGGER.info('DIALOG_WARNING = %s',DIALOG_WARNING)
        self.label = Gtk.Label.new(str=str_label)
        content_area.append(self.label)

    def dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            LOGGER.info('pressed ok in Dialog Box')
        elif response == Gtk.ResponseType.CANCEL:
            LOGGER.info('pressed cancel in Dialog Box')
            #self.label.set_text(str=f'pressed CANCEL')

        dialog.close()
'''


#main class
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

        self.hbox4 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox3.set_margin_top(5)

        self.vbox.set_margin_start(150)
        self.vbox.set_margin_top(25)
        self.vbox.set_margin_end(150)

        self.vbox1.set_margin_top(20)
        self.vbox1.set_margin_bottom(20)
        self.vbox2.set_margin_top(20)
        self.vbox2.set_margin_bottom(20)
        self.vbox3.set_margin_top(20)
        self.vbox3.set_margin_bottom(20)
        self.vbox4.set_margin_top(20)
        self.vbox4.set_margin_bottom(20)

        LOGGER.info('boxes created') 
        #---------
        self.entry = Gtk.Entry()
        self.label3 = Gtk.Label(label="")
        self.vbox3.append(self.entry)
        self.vbox3.append(self.label3)
        self.vbox.append(self.vbox3)


        self.combo = Gtk.ComboBoxText()
        self.label4 = Gtk.Label()
        self.label4.set_markup('<span font="'+dic['en']['family']
                +' '+'15'+'"' + FALLPARAM
                + 'Select Language'
                + '</span>')
        self.hbox3.append(self.label4)
        self.hbox3.append(self.combo)
        self.vbox3.append(self.hbox3)
        self.vbox.append(self.vbox3)

        LOGGER.info('textentry and drop-down created')
        #---------

        self.label1 = Gtk.Label()
        self.button1 = Gtk.FontButton.new()
        LOGGER.info('level1, button1 created')
        self.fontbutton(self.label1, self.button1, self.hbox1, self.vbox1)
        self.label2 = Gtk.Label()
        self.button2 = Gtk.FontButton.new()
        LOGGER.info('level2, button2 created')
        self.fontbutton(self.label2, self.button2, self.hbox2, self.vbox2)
        #label2 font set for en when first time open and family2 contains fontweight
        self.label2.set_markup('<span font="'+dic['en']['family2']
                +' '+FONTSIZE+'"' + FALLPARAM
                + 'Work Hard and achieve anything'
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
        LOGGER.info('slider and level_slider created')
        self.vbox4.append(self.label_slider)
        #self.hbox3.append(self.slider)
        #self.vbox4.append(self.hbox3)
        self.vbox4.append(self.slider)
        self.vbox.append(self.vbox4)


        for lang in sorted(dic,
                key = lambda x: (
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
                f'{label3_font}" {FALLPARAM}{label_lang_full_form}</span>')

        keycont = Gtk.EventControllerKey()
        keycont.connect('key-released', self.on_key_released)
        self.add_controller(keycont)

        self.set_default_size(450, 450)
        #self.set_resizable(1)
        self.set_child(self.vbox)
        #self.set_position(Gtk.WindowPosition.CENTER)

    def fontbutton(self, label, button, boxh, boxv):
        '''
        setting up initial font and text for labels and font button text updated
        '''
        LOGGER.info('fontbutton function started')
        label.set_markup('<span font="'+dic['en']['family']
                +' '+FONTSIZE+'"' + FALLPARAM
                + 'Work Hard and achieve anything'
                + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(dic['en']['family'] + ' ' + FONTSIZE)
        #button.set_language('English')
        boxh.append(button)
        boxv.append(boxh)
        boxv.append(label)
        self.vbox.append(boxv)

    def slider_changed(self, slider, button1_family, button2_family):
        LOGGER.info('slider_changed function started')
        '''
        both text labels will change it's fontsize depending upon font's slider
        '''
        LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
        #button1_family = self.button1.get_font()[:-3].strip()
        #button2_family = self.button1.get_font()[:-3].strip()
        button1_family = self.button1.get_font().rsplit(' ',1)[0]
        button2_family = self.button2.get_font().rsplit(' ',1)[0]
        LOGGER.info('self.button1_family(%s)', button1_family)
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
        LOGGER.info('label_font_change function started')
        '''
        font family and font size changes by font-button dialog
        '''
        pango_font_description = Pango.FontDescription.from_string(str=button.get_font(),)
        pango_attr_font_desc = Pango.AttrFontDesc.new(desc=pango_font_description,)
        pango_attr_list = Pango.AttrList.new()
        pango_attr_list.insert(attr=pango_attr_font_desc)
        label.set_attributes(attrs=pango_attr_list)

    def set_font(self, detect_lang, set_text):
        LOGGER.info('set_font function started')
        '''
        setting up text,
        font family depending upon which language has detected
        '''
        self.label1.set_markup('<span font="'+dic[detect_lang]['family']
                +' '+FONTSIZE+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button1.set_font(%s)',
                dic[detect_lang]['family'] +' '+FONTSIZE)
        self.button1.set_font(dic[detect_lang]['family'] +' '+FONTSIZE)
        LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
        self.label2.set_markup('<span font="'+dic[detect_lang]['family2']
                +' '+FONTSIZE+'"' + FALLPARAM
                + set_text + '</span>')
        LOGGER.info('self.button2.set_font(%s)',
                dic[detect_lang]['family2'] +' '+ FONTSIZE)
        self.button2.set_font(dic[detect_lang]['family2'] +' '+ FONTSIZE)
        LOGGER.info('self.button2.get_font(%s)',self.button2.get_font())

    def on_key_released(self, *_):
        '''
        while typing on gtk entry box..
        the langugage is detected automatically with same time and also
        setting up label3 text's font family and fontsize
        '''
        LOGGER.info('on_key_released function started')
        text = self.entry.get_text()
        lang = detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        #----
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']
                +' '+label3_font+'"' + FALLPARAM
                + label_lang_full_form + '</span>')
        #----
        #preview text means the text inside the font button dialog
        if lang in dic:
            self.button1.set_preview_text(dic[lang]['text'])
            self.button2.set_preview_text(dic[lang]['text'])
            self.set_font(lang, text)
            '''
            lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
            lc_messages_lang = lc_messages.split('_')[0]
            label_lang_full_form = langtable.language_name(
            languageId=lang, languageIdQuery=lc_messages)
            self.label3.set_markup('<span font="'+dic[lc_messages_lang]['family']
                    +' '+label3_font+'"' + FALLPARAM
                    + label_lang_full_form + '</span>')
            '''
            self.combo.handler_block(self.combo.changed_signal_id)
            for i, item in enumerate(self.combo.get_model()):
                if item[0] == lang:
                    self.combo.set_active(i)
            self.combo.handler_unblock(self.combo.changed_signal_id)
        elif not lang in dic:
            #dialog box
            #self.open_dialog(label_lang_full_form)
            #LOGGER.exception('Fonts are not installed for (%s) language', label_lang_full_form)
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

    ''' 
    def open_dialog(self, lang_full_form):
        global DIALOG_WARNING
        DIALOG_WARNING = lang_full_form
        LOGGER.info('DIALOG_WARNING = %s',DIALOG_WARNING)
        #CustomDialog is a class
        custom_dialog = CustomDialog(transient_for=self, use_header_bar=True)
        custom_dialog.present()
    '''

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
        LOGGER.info('%s is selected from drop-down',lang)
        text = dic[lang]['text']
        self.entry.set_text(text)
        #set_preview_text means - Setting the sample text for specific language that selected into the sample text field section at the bottom of the Gtk font selection dialog
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
                +' '+label3_font+'"' + FALLPARAM
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
    '''
    if not lang in dic:
        LOGGER.error(
                'lang=%s was detected but we don’t have that in dic',
                lang)
        #lang = 'en'
    '''
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

def get_random_font_family_for_language(lang: str) -> str:
    LOGGER.info('get_random_font_family_for_language function started') 
    #getting random font by python fontconfig

    try:
        LOGGER.info('entered try block')
        fonts = fontconfig.query(lang=lang) 
        fonts_family = fonts[0].family[0][1]
        fonts_style = fonts[0].style[0][1]
        LOGGER.info('random - fonconfig family = (%s) and style = (%s)', fonts_family, fonts_style)
        return fonts_family
    except Exception as error:
        LOGGER.info('entered except block')
        LOGGER.exception('error', error.__class__.__name__, error)
        return ''

#----------

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
    #jft
    #fonts = fontconfig.query(lang='ar')
    #fonts_family = fonts[0].family[0][1] 
    #fonts_style = fonts[0].style[0][1]
    #LOGGER.info('random - fonconfig family = %s and style = %s', fonts_family, fonts_style)
    for language, value in dic.items():
        family = get_default_font_family_for_language(language)
        LOGGER.info('lang=%s default family=%s', language, family)
        value['family'] = family
        #jft for label2 random font
        family2 = get_random_font_family_for_language(language)
        LOGGER.info('lang=%s random family=%s', language, family2)
        value['family2'] = family2

    LOGGER.info('dic=%s', dic)
    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)
