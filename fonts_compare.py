#!/usr/bin/python3
'''
This is my fonts-compare program for font rendering and comparing
'''
from typing import Any
from typing import List
from typing import Set
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
import freetype
import string
# pylint: disable=wrong-import-position
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk # type: ignore
gi.require_version('Pango', '1.0')
from gi.repository import Pango
from gi.repository import GLib
gi.require_version('Adw', '1')
from gi.repository import Adw
# pylint: enable=wrong-import-position

LOGGER = logging.getLogger('fonts-compare')

def parse_args() -> Any:
    '''Parse the command line arguments'''
    parser = argparse.ArgumentParser(
            add_help=False,
            description='Fonts Compare Tool')
    parser.add_argument(
            '-d', '--debug',
            action='store_true',
            default=False,
            help=('Print debug output '
                  'default: %(default)s'))
    parser.add_argument(
            '-nf', '--nofonts',
            action='store_true',
            default=False,
            help=('display languages with missing fonts'))
    parser.add_argument(
           '-l', '--lang',
            type=str,
            help=('Set language/directly open fonts-compare for a particular language from command line'))
    parser.add_argument(
           '-h', '--help',
            action='store_true',
            default=False,
            help=('Display help message'))
    return parser.parse_args()

_ARGS = parse_args()

FALLPARAM = 'fallback="false">'
FONTSIZE = '40'
LABEL3_FONT = '20'
SHOWSTYLEBOOL = False
first_font_saved = ''
lang_before_ok_response = ''
LANGDETECT_CHECKBOX = True

class CustomDialog(Gtk.Dialog):
    '''
    this class is used for displaying custom dialog window for editing labels
    '''
    def langdetect_edit_label_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''
        function to disable language detection level in edit label button
        '''
        state = self.langdetect_edit_label_checkbox.get_active()
        LOGGER.info('The switch has been switched %s', 'on' if state else 'off')
        if state:
            ##show langdetect label
            self.langdetect_edit_labels.show()
            LOGGER.info('language detection turned on - edit label')
            self.set_default_size(278, 250)
        else:
            ##hide langdetect label
            if GTK_VERSION >= (4, 9, 3):
                    self.langdetect_edit_labels.set_property("visible", False)
            else:
                self.langdetect_edit_labels.hide()
            LOGGER.info('language detection turned off - edit label')
            self.set_default_size(278, 180)

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.parent = kwargs.get('transient_for')

        self.set_title(title='Dialog Box')
        self.use_header_bar = True
        self.connect('response', self.dialog_response, parent)


        self.set_width = 278
        self.set_height = 250
        self.temp_lang_custom_dialog = ''
        self.temp_text_custom_dialog = ''

        self.add_buttons(
                '_Cancel', Gtk.ResponseType.CANCEL,
                '_OK', Gtk.ResponseType.OK,
                )
        self.btn_ok = self.get_widget_for_response(Gtk.ResponseType.OK)
        self.btn_cancel = self.get_widget_for_response(Gtk.ResponseType.CANCEL)
        self.btn_ok.get_style_context().add_class('suggested-action')
        self.btn_cancel.get_style_context().add_class('destructive-action')
        self.set_default_response(Gtk.ResponseType.OK)

        content_area = self.get_content_area()
        content_area.set_orientation(orientation=Gtk.Orientation.VERTICAL)
        content_area.set_spacing(spacing=24)
        content_area.set_margin_top(margin=12)
        content_area.set_margin_end(margin=12)
        content_area.set_margin_bottom(margin=12)
        content_area.set_margin_start(margin=12)

        self.entry_edit_labels = Gtk.Entry()
        self.label_entry_edit_labels = Gtk.Label(label="Type Here")
        self.langdetect_edit_labels = Gtk.Label(label="")
        self.langdetect_edit_label_checkbox = Gtk.CheckButton.new_with_label('Detect Language of the text')
        self.langdetect_edit_label_checkbox.set_active(True)
        self.langdetect_edit_label_checkbox.connect('toggled', self.langdetect_edit_label_checkbox_on_changed)
        content_area.append(self.label_entry_edit_labels)
        content_area.append(self.entry_edit_labels)
        content_area.append(self.langdetect_edit_labels)
        content_area.append(self.langdetect_edit_label_checkbox)

    def dialog_response(self, dialog, response, parent):
        '''
        when we click on ok and cancek in dialog window
        '''
        global LANGDETECT_CHECKBOX
        if response == Gtk.ResponseType.OK:
            LOGGER.info('pressed ok')
            text = self.entry_edit_labels.get_text()
            lang = parent.detect_language(text)
            print('checkbox landetect state:', self.langdetect_edit_label_checkbox.get_active())
            #fetch the lang_before_ok_response
            langdetect_checkbox_state = self.langdetect_edit_label_checkbox.get_active()
            LANGDETECT_CHECKBOX = langdetect_checkbox_state
            if GTK_VERSION >= (4, 9, 3):
                parent.label_button_set_after_entry_dialog_ok_newversion(text,lang, langdetect_checkbox_state)
            else:
                parent.label_button_set_after_entry_dialog_ok(text,lang, langdetect_checkbox_state)
            parent.set_default_size(300,200)
            #schedule dialog.close() to be called later
            GLib.idle_add(dialog.close)

        elif response == Gtk.ResponseType.CANCEL:
            LOGGER.info('pressed cancel')
            langdetect_checkbox_state = self.langdetect_edit_label_checkbox.get_active()
            LANGDETECT_CHECKBOX = langdetect_checkbox_state
            dialog.close()


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
        self.set_version('1.5.2')
        self.set_comments('A tool to compare fonts.')
        self.set_copyright(
                '© 2022 Sudip Shil, All Rights Reserved.')
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
        GPL-2.0-or-later
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

#custom filter
class GTKCustomFilter(Gtk.CustomFilter):
    '''
    class to filter fonts against language for gtk version 4.9.3 and above
    '''
    def __init__(self, language_code):
        super().__init__()
        self.language_code = language_code
        if '_' in language_code:
            language_code = language_code.replace('_', '-')
        self._fonts_supporting_language: Set[str] = set()
        if SHOWSTYLEBOOL:
            output = subprocess.check_output(["fc-list", ":lang=" + language_code, "family", "style"]).decode("utf-8")
            font_families = set(output.splitlines())
            for font_entry in font_families:
                font_name = font_entry.split(":")[0]
                self._fonts_supporting_language.add(font_name)
            LOGGER.info('style included')
        else:
            output = subprocess.check_output(["fc-list", ":lang=" + language_code, "family"]).decode("utf-8")
            font_families = set(output.splitlines())
            for fontname in font_families:
                self._fonts_supporting_language.add(fontname)
            LOGGER.info('family included')
        self.set_filter_func(self.font_filter)
    def font_filter(self, font_face):
        '''
        function to filter fonts for set_filter_func
        '''
        if SHOWSTYLEBOOL:
            font_pango_font_description = font_face.describe().to_string()
        else:
            font_pango_font_description = font_face.get_name()
        return self.font_support_language_filter(font_pango_font_description, self.language_code)
    #font_support_language_filter
    def font_support_language_filter(self, font, lang):
        '''
        function returns boolean value for font_filter function
        '''
        return font in self._fonts_supporting_language

class AppWindow(Gtk.ApplicationWindow): # type: ignore
    '''
    Including appwindow class to window to present
    '''
    def __init__(self, appp: Gtk.Application, language: str) -> None:
        super().__init__(application=appp)
        self.cli_language = language
        self.init_ui()

    def init_ui(self) -> None:
        '''
        init_ui contains all the containers, labels, buttons
        '''
        self.set_title('Fonts Compare')

        header_bar = Gtk.HeaderBar()
        header_bar.set_hexpand(True)
        header_bar.set_vexpand(False)
        main_menu_button = Gtk.MenuButton()
        main_menu_button.set_icon_name("open-menu-symbolic")
        main_menu_button.set_has_frame(False)
        main_menu_button.set_direction(Gtk.ArrowType.DOWN)
        header_bar.pack_end(main_menu_button)
        self._main_menu_popover = Gtk.Popover()
        main_menu_button.set_popover(self._main_menu_popover)
        self._main_menu_popover.set_autohide(True)
        self._main_menu_popover.set_position(Gtk.PositionType.BOTTOM)
        main_menu_popover_vbox = Gtk.Box()
        main_menu_popover_vbox.set_orientation(Gtk.Orientation.VERTICAL)
        main_menu_popover_vbox.set_spacing(0)

        #checkbox in menu sample text
        self.pango_sample_text_checkbox = Gtk.CheckButton.new_with_label('Pango Sample Text')
        self.pango_sample_text_checkbox.set_active(False)
        self.pango_sample_text_checkbox.connect('toggled',
                                                self.pango_sample_text_checkbox_on_changed)
        main_menu_popover_vbox.append(self.pango_sample_text_checkbox)

        #fallback in menu
        self.fallback_checkbox = Gtk.CheckButton.new_with_label('Fallback')
        self.fallback_checkbox.set_active(False)
        self.fallback_checkbox.connect('toggled', self.fallback_checkbox_on_changed)
        main_menu_popover_vbox.append(self.fallback_checkbox)

        #fontversion in menu
        if GTK_VERSION >= (4,9,3):
            self.fontversion_checkbox = Gtk.CheckButton.new_with_label('Fontversion')
            self.fontversion_checkbox.set_active(False)
            self.fontversion_checkbox.connect('toggled', self.fontversion_checkbox_on_changed)
            main_menu_popover_vbox.append(self.fontversion_checkbox)

        #hide style in menu
        if GTK_VERSION >= (4,9,3):
            self.showstyle_checkbox = Gtk.CheckButton.new_with_label('Show Style')
            self.showstyle_checkbox.set_active(False)
            self.showstyle_checkbox.connect('toggled', self.showstyle_checkbox_on_changed)
            main_menu_popover_vbox.append(self.showstyle_checkbox)

        #wrap toggle/checkbox in menu
        self.wrap_checkbox = Gtk.CheckButton.new_with_label('Wrap Text')
        self.wrap_checkbox.set_active(False)
        self.wrap_checkbox.connect('toggled', self.wrap_checkbox_on_changed)
        main_menu_popover_vbox.append(self.wrap_checkbox)

        #dark theme in menu
        self.darktheme_checkbox = Gtk.CheckButton.new_with_label('Dark Theme')
        self.darktheme_checkbox.set_active(False)
        self.darktheme_checkbox.connect('toggled', self.darktheme_checkbox_on_changed)
        main_menu_popover_vbox.append(self.darktheme_checkbox)

        #spin button in hamburger menu
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
                'value-changed',
                self.on_fontsize_adjustment_value_changed,
                self.button1_family, self.button2_family)
        main_menu_popover_vbox.append(self._fontsize_spin_button)


        self._main_menu_edit_label_button = Gtk.Button(label='Edit Text')
        self._main_menu_edit_label_button.set_has_frame(False)
        self._main_menu_edit_label_button.connect('clicked', self._on_edit_label_button_clicked)
        main_menu_popover_vbox.append(self._main_menu_edit_label_button)
        
        self._main_menu_about_button = Gtk.Button(label='About')
        self._main_menu_about_button.set_has_frame(False)
        self._main_menu_about_button.connect('clicked', self._on_about_button_clicked)
        main_menu_popover_vbox.append(self._main_menu_about_button)

        self._main_menu_quit_button = Gtk.Button(label='Quit')
        self._main_menu_quit_button.set_has_frame(False)
        self._main_menu_quit_button.connect('clicked', self._on_quit_button_clicked)
        main_menu_popover_vbox.append(self._main_menu_quit_button)

        self._main_menu_popover.set_child(main_menu_popover_vbox)

        #self._language_menu_button = Gtk.MenuButton(label='en')
        self._language_menu_button = Gtk.MenuButton(label=self.cli_language)
        self._language_menu_button.set_has_frame(False)
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
        self._language_menu_popover_scroll.set_has_frame(False)
        self._language_menu_popover_scroll.set_hexpand(True)
        self._language_menu_popover_scroll.set_vexpand(True)
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
        self.vbox.set_margin_top(5)
        self.vbox.set_margin_bottom(5)

        self.hbox_button1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox_button1.set_spacing(0)
        self.hbox_button1.props.halign = Gtk.Align.CENTER

        self.hbox_button2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox_button2.set_spacing(0)
        self.hbox_button2.props.halign = Gtk.Align.CENTER

        self.label_error = Gtk.Label()
        self.vbox.append(self.label_error)

        self.label1 = Gtk.Label()
        self.label1.set_selectable(True)
        self.label1.set_justify(Gtk.Justification.FILL)
        self.label1.set_max_width_chars(32)
        if GTK_VERSION >= (4,9,3):
            self.button1 = Gtk.FontDialog()
            self.font_dialog_button1 = Gtk.FontDialogButton()
            self.font_dialog_button1.set_dialog(self.button1)
            self.font_dialog_button1.connect('notify::font-desc', self.label_font_change_newversion, self.label1)
            self.fontbutton_newversion(self.label1, self.font_dialog_button1, self.hbox_button1)
            self.font_dialog_button1.set_level(Gtk.FontLevel.FAMILY)
            #self.custom_filter = GTKCustomFilter('en')
            self.custom_filter = GTKCustomFilter(self.cli_language)
            self.button1.set_filter(self.custom_filter)
        else:
            self.button1 = Gtk.FontButton.new()
            self.fontbutton(self.label1, self.button1, self.hbox_button1)
            self.button1.set_level(Gtk.FontChooserLevel.SIZE)
            self.button1.set_filter_func(self.font_filter)
        self.vbox.append(self.hbox_button1)
        #fontversion label1
        if GTK_VERSION >= (4,9,3):
            self.fv_label1 = Gtk.Label()
            self.vbox.append(self.fv_label1)
        self.vbox.append(self.label1)
        self.label2 = Gtk.Label()
        self.label2.set_selectable(True)
        self.label2.set_justify(Gtk.Justification.FILL)
        self.label2.set_max_width_chars(32)
        if GTK_VERSION >= (4,9,3):
            self.button2 = Gtk.FontDialog()
            self.font_dialog_button2 = Gtk.FontDialogButton()
            self.font_dialog_button2.set_dialog(self.button2)
            self.font_dialog_button2.connect('notify::font-desc', self.label_font_change_newversion, self.label2)
            self.fontbutton_newversion(self.label2, self.font_dialog_button2, self.hbox_button2)
            self.font_dialog_button2.set_level(Gtk.FontLevel.FAMILY)
            self.button2.set_filter(self.custom_filter)
        else:
            self.button2 = Gtk.FontButton.new()
            self.fontbutton(self.label2, self.button2, self.hbox_button2)
            self.button2.set_level(Gtk.FontChooserLevel.SIZE)
            self.button2.set_filter_func(self.font_filter)
        self.vbox.append(self.label2)
        #fontversion label2
        if GTK_VERSION >= (4,9,3):
            self.fv_label2 = Gtk.Label()
            self.vbox.append(self.fv_label2)
            self.fv_label1.set_property("visible", False)
            self.fv_label2.set_property("visible", False)
        self.vbox.append(self.hbox_button2)

        #temp_other_font = self.get_other_font_family_for_language('en')
        temp_other_font = self.get_other_font_family_for_language(self.cli_language)
        self.label2.set_markup('<span font="'+temp_other_font
                               +' '+FONTSIZE+'"' + FALLPARAM
                               + self.sample_text_selector('en')
                               + '</span>')
        if GTK_VERSION >= (4,9,3):
            self.font_dialog_button2.set_font_desc(Pango.font_description_from_string(temp_other_font + ' ' + FONTSIZE))
            self.button1.set_title(self.font_dialog_button1.get_font_desc().to_string())
            self.button2.set_title(self.font_dialog_button2.get_font_desc().to_string())
        else:
            self.button2.set_font(temp_other_font + ' ' + FONTSIZE)
        text = self.label1.get_text()
        lang = self.detect_language(text)
        self._currently_selected_language = lang
        LOGGER.info('label1: text=%s lang=%s', text,lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        self._language_menu_button.set_tooltip_text(label_lang_full_form)

        self.pango_sample_text_checkbox.set_active(True)
        self.pango_sample_text_checkbox.set_active(False)

        if self.is_dark_mode_enabled():
            LOGGER.info('system dark mode is on')
            LOGGER.info('Turning ON darktheme checkbox')
            self.darktheme_checkbox.set_active(True)

        self.set_default_size(300,200)
        self.set_resizable(True)
        self.set_child(self.vbox)

    def is_dark_mode_enabled(self) -> bool:
        '''
        Check if dark mode is enabled based on system preference or application settings.
        '''
        style_manager = Adw.StyleManager.get_default()
        return style_manager.get_dark()

    #font_filter
    def font_filter(self, font_family,font_face):
        '''
        function to filter fonts depending upon selected language
        '''
        font_pango_font_description = font_family.get_name()
        current_lang = self._language_menu_button.get_label()
        try:
            result = subprocess.run(["fc-list", font_pango_font_description, "lang"], encoding='utf-8', check=True, capture_output=True)
            output = ""
            output = result.stdout
            if not output.startswith(':lang='):
                return False
            #langs = output.split('=')[1].split('|')
            if output and not output.startswith(':lang='):
                return False
            langs = output.split('=')[1].split('|') if output else []
            if current_lang in langs:
                return True
            return False
        except subprocess.CalledProcessError as error:
            LOGGER.exception('Exception when calling %s: %s stderr: %s',
                             error.__class__.__name__, error, error.stderr)
            return False
        except Exception as error: # pylint: disable=broad-except
            LOGGER.exception('Exception when calling %s: %s',
                             error.__class__.__name__, error)
            return False

    #spin button font size change by adjustment increment decrement
    def on_fontsize_adjustment_value_changed(
            self,
            adjustment: Gtk.Adjustment,
            button1_family: str,
            button2_family: str) -> None:
        '''
        spin button adjustment button used for
        increase and decrease of font size of label1 and label2
        '''
        temp_label1_text = self.label1.get_text()
        temp_label2_text = self.label2.get_text()
        if GTK_VERSION >= (4, 9, 3):
            button1_family = self.font_dialog_button1.get_font_desc().to_string().rsplit(' ',1)[0]
            button2_family = self.font_dialog_button2.get_font_desc().to_string().rsplit(' ',1)[0]
            self.font_dialog_button1.set_font_desc(Pango.font_description_from_string(button1_family + ' '
                                  + str(self._fontsize_adjustment.get_value())))
            self.font_dialog_button2.set_font_desc(Pango.font_description_from_string(button2_family + ' '
                                  + str(self._fontsize_adjustment.get_value())))
        else:
            button1_family = self.button1.get_font().rsplit(' ',1)[0]
            button2_family = self.button2.get_font().rsplit(' ',1)[0]
            self.button1.set_font(button1_family + ' '
                                  + str(self._fontsize_adjustment.get_value()))
            self.button2.set_font(button2_family + ' '
                                  + str(self._fontsize_adjustment.get_value()))

        if GTK_VERSION >= (4, 9, 3):
            #setting family-style-size to label1
            pango_font_description1 = self.font_dialog_button1.get_font_desc()
            pango_font_description1.set_size(int(self._fontsize_adjustment.get_value()) * Pango.SCALE)
            pango_attr_font_description1 = Pango.AttrFontDesc.new(pango_font_description1)
            pango_attr_list = Pango.AttrList.new()
            pango_attr_list.insert(attr=pango_attr_font_description1)
            self.label1.set_attributes(attrs=pango_attr_list)
            #setting family-style-size to label2
            pango_font_description2 = self.font_dialog_button2.get_font_desc()
            pango_font_description2.set_size(int(self._fontsize_adjustment.get_value()) * Pango.SCALE)
            pango_attr_font_description2 = Pango.AttrFontDesc.new(pango_font_description2)
            pango_attr_list = Pango.AttrList.new()
            pango_attr_list.insert(attr=pango_attr_font_description2)
            self.label2.set_attributes(attrs=pango_attr_list)
        else:
            self.label1.set_markup('<span font="'+button1_family+' '
                                   +str(self._fontsize_adjustment.get_value())
                                   +'"' + FALLPARAM
                                   + temp_label1_text
                                   + '</span>')
            self.label2.set_markup('<span font="'+button2_family+' '
                                   +str(self._fontsize_adjustment.get_value())
                                   +'"' + FALLPARAM
                                   + temp_label2_text
                                   + '</span>')
        #wrapping text if font size greater than 60
        if (self.pango_sample_text_checkbox.get_active() is True) and (
                int(self._fontsize_adjustment.get_value()) > 60):
            self.label1.set_wrap(True)
            self.label2.set_wrap(True)
            self.wrap_checkbox.set_active(True)
        elif (int(self._fontsize_adjustment.get_value()) > 30) and (len(self.label1.get_text()) > 45):
            self.label1.set_wrap(True)
            self.label2.set_wrap(True)
            self.wrap_checkbox.set_active(True)
        else:
            self.label1.set_wrap(False)
            self.label2.set_wrap(False)
            self.wrap_checkbox.set_active(False)
            self.set_default_size(300,200)


    def fontbutton(
            self,
            label: Gtk.Label,
            button: Gtk.FontButton,
            boxh: Gtk.Box) -> None:
        '''
        setting up initial font and text for labels and font button text updated
        '''
        temp_label_button_font = self.get_default_font_family_for_language(self.cli_language)
        label.set_markup('<span font="'+temp_label_button_font
                         +' '+FONTSIZE+'"' + FALLPARAM
                         + self.sample_text_selector('en')
                         + '</span>')
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        button.set_font(temp_label_button_font + ' ' + FONTSIZE)
        boxh.append(button)

    @classmethod
    def label_font_change(
            cls, button: Gtk.FontButton, label: Gtk.Label) -> None:
        '''
        font family and font size changes by font-button dialog
        '''
        label.set_markup('<span font="'+button.get_font().rsplit(' ',1)[0]
                               +' '+FONTSIZE+'"' + FALLPARAM
                               + label.get_text()
                               + '</span>')

    def fontbutton_newversion(
            self,
            label: Gtk.Label,
            dialogButton,
            boxh: Gtk.Box) -> None:
        '''
        setting up initial font and text for labels and font button text updated
        '''
        temp_label_button_font = self.get_default_font_family_for_language(self.cli_language)
        label.set_markup('<span font="'+temp_label_button_font
                         +' '+FONTSIZE+'"' + FALLPARAM
                         + self.sample_text_selector('en')
                         + '</span>')
        dialogButton.set_font_desc(Pango.font_description_from_string(temp_label_button_font + ' ' + FONTSIZE))
        boxh.append(dialogButton)

    def label_font_change_newversion(
            self, dialogButton, _param_spec: Any, label: Gtk.Label) -> None:
        '''
        font family and font size changes by font-button dialog
        '''
        global FONTSIZE
        pango_font_description = dialogButton.get_font_desc()
        pango_font_description.set_size(int(FONTSIZE) * Pango.SCALE)
        pango_attr_font_description = Pango.AttrFontDesc.new(pango_font_description)
        pango_attr_list = Pango.AttrList.new()
        pango_attr_list.insert(attr=pango_attr_font_description)
        label.set_attributes(attrs=pango_attr_list)

        if self.fontversion_checkbox.get_active() is True:
            word1 = self.font_dialog_button1.get_font_desc().to_string().split()
            last_word1 = word1[-1]
            if last_word1.isdigit():
                self.fv_label1.set_markup('<span foreground='+"'green'"+ 'font="'
                                          +self.get_default_font_family_for_language('en')
                                          +' '+'8'+'"' + FALLPARAM
                                          + '<b>' + self.get_font_version(self.font_dialog_button1.get_font_desc().to_string().rsplit(' ',1)[0]) + '</b>'
                                          + '</span>')
            else:
                self.fv_label1.set_markup('<span foreground='+"'green'"+ 'font="'
                                          +self.get_default_font_family_for_language('en')
                                          +' '+'8'+'"' + FALLPARAM
                                          + '<b>' + self.get_font_version(self.font_dialog_button1.get_font_desc().to_string()) + '</b>'
                                          + '</span>')
            word2 = self.font_dialog_button2.get_font_desc().to_string().split()
            last_word2 = word2[-1]
            if last_word2.isdigit():
                self.fv_label2.set_markup('<span foreground='+"'green'"+ 'font="'
                                          +self.get_default_font_family_for_language('en')
                                          +' '+'8'+'"' + FALLPARAM
                                          + '<b>' + self.get_font_version(self.font_dialog_button2.get_font_desc().to_string().rsplit(' ',1)[0]) + '</b>'
                                          + '</span>')
            else:
                self.fv_label2.set_markup('<span foreground='+"'green'"+ 'font="'
                                          +self.get_default_font_family_for_language('en')
                                          +' '+'8'+'"' + FALLPARAM
                                          + '<b>' + self.get_font_version(self.font_dialog_button2.get_font_desc().to_string()) + '</b>'
                                          + '</span>')

    def fallback_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''
        function to change fallback as True
        '''
        global FALLPARAM
        state = self.fallback_checkbox.get_active()
        if state:
            FALLPARAM = 'fallback="true">'
            LOGGER.info('fallback checked %s',state)
        else:
            FALLPARAM = 'fallback="false">'
            LOGGER.info('fallback checked %s',state)
        LOGGER.info('version check and continue to next line')
        if GTK_VERSION >= (4, 9, 3):
            self.label1.set_markup('<span font="'+self.font_dialog_button1.get_font_desc().to_string()
                               +'"' + FALLPARAM
                               + self.label1.get_text()
                               + '</span>')
            self.label2.set_markup('<span font="'+self.font_dialog_button2.get_font_desc().to_string()
                                   +'"' + FALLPARAM
                                   + self.label2.get_text()
                                   + '</span>')
        else:
            self.label1.set_markup('<span font="'+self.button1.get_font()
                                   +'"' + FALLPARAM
                                   + self.label1.get_text()
                                   + '</span>')
            self.label2.set_markup('<span font="'+self.button2.get_font()
                                   +'"' + FALLPARAM
                                   + self.label2.get_text()
                                   + '</span>')

    def fontversion_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''                   
        function to display the fontverison of a font
        '''
        state = self.fontversion_checkbox.get_active()
        if state:
            LOGGER.info('fontversion checkbox checked')
            if GTK_VERSION >= (4, 9, 3):
                self.fv_label1.set_markup('<span foreground='+"'green'"+ 'font="'
                                          +self.get_default_font_family_for_language('en')
                                          +' '+'8'+'"' + FALLPARAM
                                          + '<b>' + self.get_font_version(self.font_dialog_button1.get_font_desc().to_string().rsplit(' ',1)[0]) + '</b>'
                                          + '</span>')

                self.fv_label2.set_markup('<span foreground='+"'green'"+ 'font="'
                                          +self.get_default_font_family_for_language('en')
                                          +' '+'8'+'"' + FALLPARAM
                                          + '<b>' + self.get_font_version(self.font_dialog_button2.get_font_desc().to_string().rsplit(' ',1)[0]) + '</b>'
                                          + '</span>')

            self.fv_label1.show()
            self.fv_label2.show()
        else:
            LOGGER.info('fontversion checkbox unchecked')
            if GTK_VERSION >= (4, 9, 3):
                self.fv_label1.set_property("visible", False)
                self.fv_label2.set_property("visible", False)
        self._main_menu_popover.popdown()
        self.set_default_size(300,200)

    def get_font_version(self, font_name):
        #getting fontpath from fontfamily
        fc_list_command = ['fc-list', font_name, 'file']
        result = subprocess.run(fc_list_command, capture_output=True, text=True)
        output_line = result.stdout.strip()
        if len(output_line) == 0:
            print("Fontpath not found")
            return 'No fontversion found'
        font_file_path = output_line.split(':')[0]
        LOGGER.info('font_path: %s',font_file_path)

        # Getting font version using Freetype
        face = freetype.Face(font_file_path)
        num_name_strings = face.sfnt_name_count
        version_string = None
        for index in range(num_name_strings):
            name_string = face.get_sfnt_name(index)
            if name_string.name_id == 5:  # Font version name ID
                version_string = name_string.string.decode('utf-8')
                version_string = version_string.strip()
                break
        cleaned_version_string = self.clean_string(version_string)
        LOGGER.info('freetype_version: %s',cleaned_version_string)
        return cleaned_version_string

    #clean non-printable letters from freetype returned string
    def clean_string(self,s):
        return ''.join(filter(lambda x: x in string.printable, s)).strip()

    def showstyle_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''
        function to wrap labels as True
        '''
        state = self.showstyle_checkbox.get_active()
        global SHOWSTYLEBOOL
        if state:
            LOGGER.info('showstyle checked %s',state)
            SHOWSTYLEBOOL = True
            if GTK_VERSION >= (4,9,3):
                self.font_dialog_button1.set_level(Gtk.FontLevel.FONT)
                self.font_dialog_button2.set_level(Gtk.FontLevel.FONT)
        else:
            SHOWSTYLEBOOL = False
            LOGGER.info('showstyle unchecked %s',state)
            if GTK_VERSION >= (4,9,3):
                self.font_dialog_button1.set_level(Gtk.FontLevel.FAMILY)
                self.font_dialog_button2.set_level(Gtk.FontLevel.FAMILY)
 
        if self.pango_sample_text_checkbox.get_active() is False: 
            self.pango_sample_text_checkbox.set_active(True)
            self.pango_sample_text_checkbox.set_active(False)
        else:
            self.pango_sample_text_checkbox.set_active(False)
            self.pango_sample_text_checkbox.set_active(True)

    def wrap_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''
        function to wrap labels as True
        '''
        state = self.wrap_checkbox.get_active()
        if state:
            LOGGER.info('wrap checked %s',state)
            self.label1.set_wrap(True)
            self.label2.set_wrap(True)
        else:
            LOGGER.info('wrap unchecked %s',state)
            self.label1.set_wrap(False)
            self.label2.set_wrap(False)

    def darktheme_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''
        function to enable dark theme as True
        '''
        state = self.darktheme_checkbox.get_active()
        if state:
            LOGGER.info("Dark Theme enabled")
            style_manager = Adw.StyleManager.get_default()
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            LOGGER.info("Dark Theme disabled")
            style_manager = Adw.StyleManager.get_default()
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        self._main_menu_popover.popdown()

    def pango_sample_text_checkbox_on_changed(
            self,
            _checkbutton: Gtk.CheckButton) -> None:
        '''
        function to change sample string depends upon toogle switch
        '''
        global FONTSIZE
        LOGGER.info("font before pango sample text checkbox clicked")
        LOGGER.info("fontbutton1:- %s, fontsize:- %s", self.font_dialog_button1.get_font_desc().to_string(), FONTSIZE)
        LOGGER.info("fontbutton2:- %s, fontsize:- %s", self.font_dialog_button2.get_font_desc().to_string(), FONTSIZE)
        state = self.pango_sample_text_checkbox.get_active()
        LOGGER.info('The switch has been switched %s', 'on' if state else 'off')
        if state:
            FONTSIZE = '20'
            LOGGER.info('pango font = %s',FONTSIZE)
        else:
            FONTSIZE = '40'
            LOGGER.info('langtable font = %s',FONTSIZE)
        components1 = self.font_dialog_button1.get_font_desc().to_string().split()
        components2 = self.font_dialog_button2.get_font_desc().to_string().split()
        if not components1[-1].isdigit():
            tempfont1 = f"{self.font_dialog_button1.get_font_desc().to_string()} {FONTSIZE}"
            self.font_dialog_button1.set_font_desc(Pango.font_description_from_string(tempfont1))
            LOGGER.info("font after changing font from fontbutton1")
            LOGGER.info("fontbutton1:- %s, fontsize:- %s", self.font_dialog_button1.get_font_desc().to_string(), FONTSIZE)
            LOGGER.info("fontbutton2:- %s, fontsize:- %s", self.font_dialog_button2.get_font_desc().to_string(), FONTSIZE)
        if not components2[-1].isdigit():
            tempfont2 = f"{self.font_dialog_button2.get_font_desc().to_string()} {FONTSIZE}"
            self.font_dialog_button2.set_font_desc(Pango.font_description_from_string(tempfont2))
            LOGGER.info("font after changing font from fontbutton2")
            LOGGER.info("fontbutton1:- %s, fontsize:- %s", self.font_dialog_button1.get_font_desc().to_string(), FONTSIZE)
            LOGGER.info("fontbutton2:- %s, fontsize:- %s", self.font_dialog_button2.get_font_desc().to_string(), FONTSIZE)
        #instant label1 and label2 change after switch change
        if GTK_VERSION >= (4, 9, 3):
            self.label1.set_markup('<span font="'+self.font_dialog_button1.get_font_desc().to_string().rsplit(' ',1)[0]
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(
                                       self._language_menu_button.get_label())
                                   + '</span>')
            self.font_dialog_button1.set_font_desc(Pango.font_description_from_string(self.font_dialog_button1.get_font_desc().to_string().rsplit(' ',1)[0] + ' ' + FONTSIZE))
            self.label2.set_markup('<span font="'+self.font_dialog_button2.get_font_desc().to_string().rsplit(' ',1)[0]
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(
                                       self._language_menu_button.get_label())
                                   + '</span>')
            LOGGER.info('lang from language list: %s', self._language_menu_button.get_label())
            self.font_dialog_button2.set_font_desc(Pango.font_description_from_string(self.font_dialog_button2.get_font_desc().to_string().rsplit(' ',1)[0] + ' ' + FONTSIZE))
        else:
            self.label1.set_markup('<span font="'+self.button1.get_font().rsplit(' ',1)[0]
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(
                                       self._language_menu_button.get_label())
                                   + '</span>')
            self.button1.set_font(self.button1.get_font().rsplit(' ',1)[0] + ' ' + FONTSIZE)
            self.label2.set_markup('<span font="'+self.button2.get_font().rsplit(' ',1)[0]
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + self.sample_text_selector(
                                       self._language_menu_button.get_label())
                                   + '</span>')
            LOGGER.info('lang from language list: %s', self._language_menu_button.get_label())
            self.button2.set_font(self.button2.get_font().rsplit(' ',1)[0] + ' ' + FONTSIZE)

        self._fontsize_adjustment.set_value(int(FONTSIZE))
        self.set_default_size(300,200)
        self._main_menu_popover.popdown()
        LOGGER.info("font after pango sample text checkbox clicked")
        LOGGER.info("fontbutton1:- %s, fontsize:- %s", self.font_dialog_button1.get_font_desc().to_string(), FONTSIZE)
        LOGGER.info("fontbutton2:- %s, fontsize:- %s", self.font_dialog_button2.get_font_desc().to_string(), FONTSIZE)

    def sample_text_selector(self, lang: str) -> str:
        '''
        sample text will be selected by either Pango or Langtable
        '''
        if self.pango_sample_text_checkbox.get_active():
            #True - Pango sample text
            sample_text = str(Pango.Language.get_sample_string(
                Pango.language_from_string (lang)))
            return sample_text
        #False - Langtable sample text
        sample_text = str(langtable.language_name(
            languageId=lang, languageIdQuery=lang))
        return sample_text


    def set_font(self, detect_lang: str, set_text: str) -> None:
        '''
        setting up text,
        font family depending upon which language has detected
        '''
        temp_label1_font = self.get_default_font_family_for_language(detect_lang)
        self.label1.set_markup('<span font="'+temp_label1_font
                               +' '+str(int(self._fontsize_adjustment.get_value()))+'"' + FALLPARAM
                               + set_text + '</span>')
        LOGGER.info('label1 text now: %s',self.label1.get_text())
        if GTK_VERSION >= (4, 9, 3):
            LOGGER.info('self.font_dialog_button1.set_font(%s)',
                        temp_label1_font +' '+str(int(self._fontsize_adjustment.get_value())))
            self.font_dialog_button1.set_font_desc(Pango.font_description_from_string(temp_label1_font +' '+str(int(self._fontsize_adjustment.get_value()))))
            LOGGER.info('self.font_dialog_button1.get_font(%s)',self.font_dialog_button1.get_font_desc().to_string())
            temp_label2_font = self.get_other_font_family_for_language(detect_lang)
            self.label2.set_markup('<span font="'+temp_label2_font
                                   +' '+str(int(self._fontsize_adjustment.get_value()))+'"' + FALLPARAM
                                   + set_text + '</span>')
            LOGGER.info('label2 text now: %s',self.label2.get_text())
            LOGGER.info('self.font_dialog_button2.set_font(%s)',
                        temp_label2_font +' '+ str(int(self._fontsize_adjustment.get_value())))
            self.font_dialog_button2.set_font_desc(Pango.font_description_from_string(temp_label2_font +' '
                                  + str(int(self._fontsize_adjustment.get_value()))))
            LOGGER.info('self.font_dialog_button2.get_font(%s)',self.font_dialog_button2.get_font_desc().to_string())
        else:
            LOGGER.info('self.button1.set_font(%s)',
                        temp_label1_font +' '+str(int(self._fontsize_adjustment.get_value())))
            self.button1.set_font(temp_label1_font +' '+str(int(self._fontsize_adjustment.get_value())))
            LOGGER.info('self.button1.get_font(%s)',self.button1.get_font())
            temp_label2_font = self.get_other_font_family_for_language(detect_lang)
            self.label2.set_markup('<span font="'+temp_label2_font
                                   +' '+str(int(self._fontsize_adjustment.get_value()))+'"' + FALLPARAM
                                   + set_text + '</span>')
            LOGGER.info('label2 text now: %s',self.label2.get_text())
            LOGGER.info('self.button2.set_font(%s)',
                        temp_label2_font +' '+ str(int(self._fontsize_adjustment.get_value())))
            self.button2.set_font(temp_label2_font +' '
                                  + str(int(self._fontsize_adjustment.get_value())))
            LOGGER.info('self.button2.get_font(%s)',self.button2.get_font())
        self.set_default_size(300,200)

    def on_entry_activate_enter_pressed_ok_signal(self, widget, custom_dialog):
        '''
        when enter key pressed after editing  entry then ok button automatically will be pressed
        '''
        custom_dialog.response(Gtk.ResponseType.OK)

    def _on_edit_label_button_clicked(self, _button: Gtk.Button) -> None:
        '''The “Edit Label” button has been clicked'''
        LOGGER.debug('Edit Label button clicked')
        self._main_menu_popover.popdown()
        #update global variable lang_before_ok_response = current selected dropdown language before changing
        global lang_before_ok_response
        lang_before_ok_response = self._language_menu_button.get_label()
        self.custom_dialog = CustomDialog(self, transient_for=self, use_header_bar=True)
        self.custom_dialog.entry_edit_labels.changed_signal_id = self.custom_dialog.entry_edit_labels.connect(
                'notify::text', self.on_entry_changed)
        self.custom_dialog.entry_edit_labels.connect("activate", self.on_entry_activate_enter_pressed_ok_signal, self.custom_dialog)
        self.custom_dialog.entry_edit_labels.set_text(self.label1.get_text())
        self.custom_dialog.entry_edit_labels.set_position(-1)
        self.custom_dialog.entry_edit_labels.grab_focus_without_selecting()
        text = self.custom_dialog.entry_edit_labels.get_text()
        lang = self.detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        global LANGDETECT_CHECKBOX
        self.custom_dialog.langdetect_edit_label_checkbox.set_active(LANGDETECT_CHECKBOX)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        LOGGER.info('label_lang full form=%s',label_lang_full_form)
        self._language_menu_button.set_tooltip_text(label_lang_full_form)
        self.custom_dialog.langdetect_edit_labels.set_markup(
                '<span font="'
                +self.get_default_font_family_for_language(lc_messages_lang)
                +' '+'15'+'"' + FALLPARAM
                + label_lang_full_form + '</span>')
        self.custom_dialog.present()


    def _on_about_button_clicked(self, _button: Gtk.Button) -> None:
        '''The “About” button has been clicked'''
        LOGGER.debug('About button clicked')
        self._main_menu_popover.popdown()
        FontsCompareAboutDialog()

    def _on_quit_button_clicked(self, _button: Gtk.Button) -> None:
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
        filter_text = self.search_entry.get_text()
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
        listbox.set_activate_on_single_click(False)
        rows = []
        filter_words = remove_accents(filter_text.lower()).split()
        currently_selected_visible = False
        for language_id in sorted(list_languages()):
            text_to_match = locale_text_to_match(language_id)
            filter_match = True
            text_to_match_words = text_to_match.split(' ')
            text_to_match_words = [element.replace("(","") for element in text_to_match_words if element]
            text_to_match_words = [element.replace(")","") for element in text_to_match_words if element]
            str_filter_words = ' '.join([str(elem) for elem in filter_words])
            length = len(str_filter_words)
            make_list = []
            for ele in text_to_match_words:
                ele_str = ""
                i=0
                while (i != length and len(str(ele)) >= length):
                    ele_str += ele[i]
                    i += 1
                make_list.append(ele_str)
            if str_filter_words not in make_list:
                filter_match = False
            if filter_match:
                if language_id != self._currently_selected_language:
                    self._language_menu_popover_language_ids.append(language_id)
                    rows.append(
                            self._language_menu_popover_listbox_fill_row(language_id))
                else:
                    self._language_menu_popover_language_ids.insert(0, language_id)
                    rows.insert(0, self._language_menu_popover_listbox_fill_row(language_id))
                    currently_selected_visible = True
        for row in rows:
            label = Gtk.Label()
            label.set_text(row)
            label.set_xalign(0)
            listbox.append(label)
        if currently_selected_visible:
            listbox.select_row(listbox.get_row_at_index(0))
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
        self._currently_selected_language = language_id
        self._language_menu_popover.popdown()
        self._language_menu_button.set_label(language_id)
        if GTK_VERSION >= (4, 9, 3):
            current_lang = self._language_menu_button.get_label()
            self.custom_filter = GTKCustomFilter(current_lang)
            self.button1.set_filter(self.custom_filter)
            self.button2.set_filter(self.custom_filter)
        else:
            self.button1.set_filter_func(self.font_filter)
            self.button2.set_filter_func(self.font_filter)
        self._language_menu_popover_language_ids = []
        LOGGER.info('language selected from menu = %s', language_id)
        text = self.sample_text_selector(language_id)
        self.custom_dialog = CustomDialog(self, transient_for=self, use_header_bar=True)
        self.custom_dialog.entry_edit_labels.set_text(text)
        self.custom_dialog.entry_edit_labels.set_position(-1)
        self.custom_dialog.entry_edit_labels.grab_focus_without_selecting()
        if GTK_VERSION >= (4, 9, 3):
            LOGGER.info('no set_preview function for font_dialog')
            #self.button1.set_preview_text(text)
            #self.button2.set_preview_text(text)
        else:
            self.button1.set_preview_text(text)
            self.button2.set_preview_text(text)
        self.set_font(language_id, text)
        #detect language by langdetect
        text = self.custom_dialog.entry_edit_labels.get_text()
        lang = self.detect_language(text)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang,
                languageIdQuery=lc_messages)
        LOGGER.debug('label_lang_full_form=%s', label_lang_full_form)
        self._language_menu_button.set_tooltip_text(label_lang_full_form)
        if self.fontversion_checkbox.get_active() is True:
            self.fontversion_checkbox.set_active(False)
            self.fontversion_checkbox.set_active(True)

    def _on_language_menu_popover_show(self, popover: Gtk.Popover) -> None:
        '''Called when the language menu popover is shown'''
        LOGGER.debug('Language menu popover is shown')
        if popover is None:
            LOGGER.error('popover is None, should never happen')
            return
        vbox_language_dropdown = Gtk.Box()
        vbox_language_dropdown.set_orientation(Gtk.Orientation.VERTICAL)
        label = Gtk.Label()
        label.set_text('Use language')
        label.set_halign(Gtk.Align.FILL)
        vbox_language_dropdown.append(label)
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_can_focus(True)
        self.search_entry.set_halign(Gtk.Align.FILL)
        vbox_language_dropdown.append(self.search_entry)
        self.search_entry.changed_signal_id = self.search_entry.connect(
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
        vbox_language_dropdown.append(self._language_menu_popover_scroll)
        popover.set_child(vbox_language_dropdown)
        self.search_entry.grab_focus()

    def label_button_set_after_entry_dialog_ok(self, text:str, lang:str, langdetect_checkbox_state: bool):
        self.label1.set_text(text)
        self.label2.set_text(text)
        global lang_before_ok_response
        if lang_before_ok_response == lang:
            #previously selected and current detected lang are same - so no change in font for both buttons
            LOGGER.info('no change in font for both buttons')
        elif lang in list_dropdown and langdetect_checkbox_state == True:
            self.button1.set_preview_text(langtable.language_name(
                languageId=lang, languageIdQuery=lang))
            self.button2.set_preview_text(langtable.language_name(
                languageId=lang, languageIdQuery=lang))
            self.set_font(lang, text)
            self._language_menu_button.set_label(lang)
            self.button1.set_filter_func(self.font_filter)
            self.button2.set_filter_func(self.font_filter)
        elif not lang in list_dropdown and langdetect_checkbox_state == True:
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

    def label_button_set_after_entry_dialog_ok_newversion(self, text:str, lang:str, langdetect_checkbox_state: bool):
        self.label1.set_text(text)
        self.label2.set_text(text)
        global lang_before_ok_response
        if lang_before_ok_response == lang:
            #previously selected and current detected lang are same - so no change in font for both buttons
            LOGGER.info('no change in font for both buttons')
        elif lang in list_dropdown and langdetect_checkbox_state == True:
            #self.button1.set_preview_text(langtable.language_name(
            #    languageId=lang, languageIdQuery=lang))
            #self.button2.set_preview_text(langtable.language_name(
            #    languageId=lang, languageIdQuery=lang))
            self.set_font(lang, text)
            self._language_menu_button.set_label(lang)
            current_lang = self._language_menu_button.get_label()
            self.custom_filter = GTKCustomFilter(current_lang)
            self.button1.set_filter(self.custom_filter)
            self.button2.set_filter(self.custom_filter)
        elif not lang in list_dropdown and langdetect_checkbox_state == True:
            self.label1.set_markup('<span font="'
                                   +self.get_default_font_family_for_language(lang)
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + text + '</span>')
            LOGGER.info('self.font_dialog_button1.set_font(%s)',
                        self.get_default_font_family_for_language(lang)
                        +' '+FONTSIZE)
            self.font_dialog_button1.set_font_desc(Pango.font_description_from_string(
                    self.get_default_font_family_for_language(lang)
                    +' '+FONTSIZE))
            LOGGER.info('self.font_dialog_button1.get_font(%s)',self.font_dialog_button1.get_font().to_string())
            self.label2.set_markup('<span font="'
                                   +self.get_default_font_family_for_language(lang)
                                   +' '+FONTSIZE+'"' + FALLPARAM
                                   + text + '</span>')
            LOGGER.info('self.font_dialog_button2.set_font_desc(%s)',
                        self.get_default_font_family_for_language(lang)
                        +' '+ FONTSIZE)
            self.font_dialog_button2.set_font_desc(Pango.font_description_from_string(
                    self.get_default_font_family_for_language(lang)
                    +' '+ FONTSIZE))
            LOGGER.info('self.font_dialog_button2.get_font_desc(%s)',self.font_dialog_button2.get_font_desc().to_string())

    def on_entry_changed(self, widget: Gtk.Entry, _property_spec: Any) -> None:
        '''Called when the text in the entry has changed.

        While typing on gtk entry box, the language is detected
        automatically time and then the font family and fontsize to
        display the text on label_langdetect is changed accordingly.
        '''
        text = self.custom_dialog.entry_edit_labels.get_text()
        lang = self.detect_language(text)
        LOGGER.info('text=%s lang=%s', text, lang)
        lc_messages = locale.getlocale(locale.LC_MESSAGES)[0]
        lc_messages_lang = 'en'
        if lc_messages:
            lc_messages_lang = lc_messages.split('_')[0]
        label_lang_full_form = langtable.language_name(
                languageId=lang, languageIdQuery=lc_messages)
        LOGGER.info('label_lang full form=%s',label_lang_full_form)
        self._language_menu_button.set_tooltip_text(label_lang_full_form)
        self.custom_dialog.langdetect_edit_labels.set_markup(
                '<span font="'
                +self.get_default_font_family_for_language(lc_messages_lang)
                +' '+'15'+'"' + FALLPARAM
                + label_lang_full_form + '</span>')
        self.custom_dialog.temp_text_custom_dialog = text
        self.custom_dialog.temp_lang_custom_dialog = lang

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
        global first_font_saved
        first_font_saved = ''
        lang = lang.replace('_','-')
        LOGGER.info('language: %s',lang)
        fc_match_binary = shutil.which('fc-match')
        if not fc_match_binary:
            return ''
        try:
            result = subprocess.run(
                    [fc_match_binary, f':lang={lang}', 'family', 'style', 'file', 'familylang'],
                    encoding='utf-8', check=True, capture_output=True,
                    env={'LC_ALL': lang.replace('-', '_')})
            pattern = re.compile(r'^(?P<families>.*?(?=:familylang=|$))(?::familylang=(?P<familylang>.*?))?:style=.*$')
            match = pattern.match(result.stdout.strip())
            if not match:
                LOGGER.error('Regexp did not match')
                return ''
            families = match.group('families').split(',')
            familylang = match.group('familylang').split(',') if match.group('familylang') else []
            LOGGER.info('default font families=%s', families)
            LOGGER.info('default familylang=%s', familylang)
            last_family = ''
            if families:
                current_lang = self._language_menu_button.get_label()
                if current_lang in str(locale.getlocale(locale.LC_MESSAGES)[0]):
                    count=0
                    for i in familylang:
                        if str(i) in str(locale.getlocale(locale.LC_MESSAGES)[0]):
                            last_family = families[count]
                            LOGGER.info('locale lang = %s',locale.getlocale(locale.LC_MESSAGES)[0])
                            LOGGER.info('selected default font = %s',last_family)
                            first_font_saved = last_family
                            LOGGER.info('first button font = %s', first_font_saved)
                            return last_family
                    if last_family == '':
                        last_family = families[-1:][0]
                        LOGGER.info('selected default font = %s',last_family)
                        first_font_saved = last_family
                        LOGGER.info('first button font = %s', first_font_saved)
                        return last_family
                else:
                    last_family = families[-1:][0]
                    first_font_saved = last_family
                    LOGGER.info('first button font = %s', first_font_saved)
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

    #----------selecting other font for label2

    def get_other_font_family_for_language(self, lang: str) -> str:
        '''
        getting a other font using fc-list
        '''
        global first_font_saved
        lang = lang.replace('_','-')
        fc_list_binary = shutil.which('fc-list')
        if not fc_list_binary:
            return ''
        try:
            result1 = subprocess.run(
                    [fc_list_binary, f':lang={lang}:fontformat=TrueType', 'family', 'style', 'familylang'],
                    encoding='utf-8', check=True, capture_output=True)
            fonts_listed1 = result1.stdout.strip().split('\n')
            result2 = subprocess.run(
                    [fc_list_binary, f':lang={lang}:fontformat=CFF', 'family', 'style', 'familylang'],
                    encoding='utf-8', check=True, capture_output=True)
            fonts_listed2 = result2.stdout.strip().split('\n')
            fonts_listed = fonts_listed1 + fonts_listed2
            list_unfilter_other_font = [x for x in fonts_listed
                                        if x and not ('Droid' in x or 'STIX' in x)] #--if x and-- to exclude empty items 
            #selecting second font from fc-list
            #but the second font should not match the first font
            LOGGER.info('first button font = %s', first_font_saved)
            other_font = ''
            if len(list_unfilter_other_font) == 1:
                other_font = list_unfilter_other_font[0]
            elif len(list_unfilter_other_font) > 1:
                LOGGER.info("Number of fonts in list_unfilter_other_font: %d", len(list_unfilter_other_font))
                for font in list_unfilter_other_font:
                    LOGGER.info('font which may have comma separated multiple fonts: %s', font)
                    font_temp = str(font)
                    font_temp = font_temp.split(':familylang')[0]
                    if ',' in font_temp:
                        #eg. Noto Sans Tamil,Noto Sans Tamil
                        font_temp = font_temp.split(',')[0].strip()
                    if (first_font_saved not in font_temp):
                        #sometimes fontconfig includes style in family name
                        #eg. Noto Sans Tamil is same Noto Sans Tamil Condensed
                        other_font = font
                        LOGGER.info('resulted font without having multiple families - style included: %s', font)
                        LOGGER.info('resulted font without having multiple families - style not included: %s', font_temp)
                        break
                if not other_font:
                    if ',' in other_font:
                        other_font = other_font.split(',')[0].strip()
                    other_font = list_unfilter_other_font[1]
            LOGGER.info('selected other list from fc-list = %s',other_font)
            if other_font:
                #diable error label when font available
                if GTK_VERSION >= (4, 9, 3):
                    self.label_error.set_property("visible", False)
                else:
                    self.label_error.hide()
            else:
                LOGGER.info('fonts are not installed for %s language',lang)
                #error level show no font installed
                label_error_text = "NOTE : fonts are not installed for " + lang + " language"
                self.label_error.set_markup('<span foreground='+"'red'"+ 'font="'
                                            +self.get_default_font_family_for_language('en')
                                            +' '+'10'+'"' + FALLPARAM
                                            + '<b>' + label_error_text + '</b>'
                                            + '</span>')
                self.label_error.show()
                return ''
            #sometimes other_font doesnot contain any style then error arises
            if other_font.find(":style") != -1:
                pattern = re.compile(r'^(?P<families>.*?(?=:familylang=|$))(?::familylang=(?P<familylang>.*?))?:style=.*$')
            else:
                pattern = re.compile(r'^(?P<families>.*?(?=:familylang=|$))(?::familylang=(?P<familylang>.*?))')
            match = pattern.match(other_font)
            if not match:
                LOGGER.error('Regexp did not match %s', result.stdout.strip())
                return ''
            families = match.group('families').split(',')
            familylang = match.group('familylang').split(',')
            LOGGER.info('Random font families=%s', families)
            LOGGER.info('Random font familylang=%s', familylang)
            last_family = ''
            if families:
                current_lang = self._language_menu_button.get_label()
                if current_lang in str(locale.getlocale(locale.LC_MESSAGES)[0]):
                    count=0
                    for i in familylang:
                        if str(i) in str(locale.getlocale(locale.LC_MESSAGES)[0]):
                            last_family = families[count]
                            LOGGER.info('locale lang = %s',locale.getlocale(locale.LC_MESSAGES)[0])
                            LOGGER.info('selected default font = %s',last_family)
                            return last_family
                    if last_family == '':
                        last_family = families[-1:][0]
                        LOGGER.info('selected default font = %s',last_family)
                        return last_family
                else:
                    last_family = families[0]
                    LOGGER.info('selected other font before confirm = %s',last_family)
            if not last_family:
                return ''
            LOGGER.info('selected other font confirm = %s',last_family)
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

def on_activate(application: Gtk.Application, language: str) -> None:
    '''
    activating the application by adding the application into gtk window
    '''
    win = AppWindow(application, language)
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
    languages = [x for x in languages
                 if not '_' in x]
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
    languages = list_languages_fontconfig()
    for lang in list_languages_glibc():
        if lang not in languages:
            languages.append(lang)
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
    dic_language_alternative_names = {
            'bn':['Bengali', 'bn_IN', 'bn_BD','indic','india'],
            'bn_IN':['Bengali', 'bn_IN', 'bn_BD','indic','india'],
            'bn_BD':['Bengali', 'bn_IN', 'bn_BD','indic','india'],
            'gu':['Gujarati','Gujerati','Gujrati','indic','india'],
            'ja':['japanese','jp','cjk'], 'ko':['korean','ko','cjk'],
            'hi':['Devanagari','hindi','hindu','Hindoostani', 'Hindostani','indic','india'],
            'ml':['malayalam','meera','indic','india'],
            'mr':['marathi','maratha','shivaji','ganesh','indic','india'],
            'or':['oriya','odia','indic','india'],
            'pa':['panjabi','punjabi','gurmukhi','indic','india'],
            'ks':['Kashmiri','Kashmir','indic','india'],
            'brx':['BODO','india','indic'],
            'doi':['Dogri','india','indic'],
            'kn':['Kannada','india','indic'],
            'kok':['Konkani','india','indic'],
            'mai':['Maithili','india','indic'],
            'mni':['Manipuri','india','indic'],
            'ne':['Nepali','india','indic'],
            'ta':['Tamil','india','indic'],
            'te':['Telugu','india','indic'],
            'sat':['Santali','india','indic'],
            'sd':['Sindhi','india','indic'],
            'ur':['Urdu','india','indic'],
            'as':['Assamese','Assam','india','indic']}
    effective_lc_messages = get_effective_lc_messages()
    text_to_match = locale_id.replace(' ', '')
    query_languages = [effective_lc_messages, locale_id, 'en']
    for query_language in query_languages:
        if query_language:
            text_to_match += ' ' + langtable.language_name(
                    languageId=locale_id,
                    languageIdQuery=query_language)
    if locale_id in dic_language_alternative_names.keys():
        text_to_match += ' ' + ' '.join([str(ele) for ele in dic_language_alternative_names[locale_id] if ele])
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

def parse_locale(locale_received, list_dropdown, locales) -> str:
    lang_locale = locale_received.split('.')[0]
    if lang_locale in list_dropdown:
        return lang_locale
    elif '-' in lang_locale or '_' in lang_locale:
        lang_code = lang_locale.split('-')[0] if '-' in lang_locale else lang_locale.split('_')[0]
        if lang_code in list_dropdown:
            return lang_code
        else:
            print("Input language should be supported by fontconfig")
            sys.exit()
    elif lang_locale in locales:
        #use locales list, if lang_locale in locales
        #then lang_locale set to en
        #because all locales are not in fontconfig
        lang_locale = 'en'
        return lang_locale
    else:
        print("Unsupported locale setting. Falling back to C locale")
        lang_locale = 'en'
        return lang_locale

def parse_lc_all_lang(list_dropdown) -> str:
    '''Parse the LC_ALL environment variable for language'''
    lc_all = os.environ.get('LC_ALL', '')
    lang_var = os.environ.get('LANG', '')
    output = subprocess.check_output(['locale', '-a']).decode('utf-8').splitlines()
    locales = [locale.split('.')[0] for locale in output]
    if lc_all:
        return parse_locale(lc_all, list_dropdown, locales)
    elif lang_var:
        return parse_locale(lang_var, list_dropdown, locales)
    else:
        #if system locale is different by default and not mentioned by LC_ALL
        default_locale_tuple = locale.getlocale()
        if default_locale_tuple[0]:
            default_locale = default_locale_tuple[0].split('.')[0]
            if default_locale in list_dropdown:
                return default_locale
            elif '-' in default_locale or '_' in default_locale:
                default_lang_code = default_locale.split('-')[0] if '-' in default_locale else default_locale.split('_')[0]
                if default_lang_code in list_dropdown:
                    return default_lang_code
                else:
                    print("Unsupported locale setting. Falling back to C locale")
                    return 'en'
        else:
            return 'en'#worst case
    return 'en' #default to 'en' if nothing matches

if __name__ == '__main__':
    list_dropdown = sorted(list_languages())
    os.environ['LC_CTYPE'] = 'C.UTF-8'
    os.environ['LC_MESSAGES'] = 'C.UTF-8'
    os.environ['LC_COLLATE'] = 'C.UTF-8'
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("Unsupported locale setting. Falling back to C locale")
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    cli_language = parse_lc_all_lang(list_dropdown)
    if _ARGS.debug:
        LOG_HANDLER = logging.StreamHandler(stream=sys.stderr)
        LOG_FORMATTER = logging.Formatter(
                '%(asctime)s %(filename)s '
                'line %(lineno)d %(funcName)s %(levelname)s: '
                '%(message)s')
        LOG_HANDLER.setFormatter(LOG_FORMATTER)
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.addHandler(LOG_HANDLER)
    elif _ARGS.nofonts:
        #call nofonts function
        print('Fonts of these languages are not installed in your system')
        print('checking...please wait...')
        #list_dropdown = sorted(list_languages())
        lang_with_nofonts_installed = []
        for i in list_dropdown:
            lang = i.replace('_','-')
            fc_list_binary = shutil.which('fc-list')
            if not fc_list_binary:
                sys.exit()
            try:
                result1 = subprocess.run(
                        [fc_list_binary, f':lang={lang}:fontformat=TrueType', 'family', 'style', 'familylang'],
                        encoding='utf-8', check=True, capture_output=True)
                fonts_listed1 = result1.stdout.strip().split('\n')
                result2 = subprocess.run(
                        [fc_list_binary, f':lang={lang}:fontformat=CFF', 'family', 'style', 'familylang'],
                        encoding='utf-8', check=True, capture_output=True)
                fonts_listed2 = result2.stdout.strip().split('\n')
                fonts_listed = fonts_listed1 + fonts_listed2
                list_unfilter_other_font = [x for x in fonts_listed
                                            if x and not ('Droid' in x or 'STIX' in x)]
                if not list_unfilter_other_font:
                    lang_with_nofonts_installed.append(lang)
            except FileNotFoundError as error:
                LOGGER.exception('Exception when calling %s: %s: %s',
                                 fc_list_binary, error.__class__.__name__, error)
                sys.exit()
            except subprocess.CalledProcessError as error:
                LOGGER.exception('Exception when calling %s: %s: %s stderr: %s',
                                 fc_list_binary,
                                 error.__class__.__name__, error, error.stderr)
                sys.exit()
            except Exception as error: # pylint: disable=broad-except
                LOGGER.exception('Exception when calling %s: %s: %s',
                                 fc_list_binary, error.__class__.__name__, error)
                sys.exit()
        print(lang_with_nofonts_installed)
        sys.exit()
    elif _ARGS.lang:
        cli_language = _ARGS.lang
        if '-' in cli_language or '_' in cli_language:
            if '-' in cli_language:
                (f,r) = cli_language.split('-', maxsplit=1)
            else:
                (f,r) = cli_language.split('_', maxsplit=1)
            cli_language = f + '_' + r.upper()
            if cli_language not in list_dropdown:
                cli_language = cli_language.split('_')[0]
        if cli_language in list_dropdown:
            print("initialize fonts-compare with ",cli_language)
        else:
            print('unsupported language is entered')
            print('printing list of languages supported by fontconfig')
            print(list_dropdown)
            sys.exit()
    elif _ARGS.help:
        print('Usage: fonts-compare [OPTIONS]')
        print('[Options]:')
        print(' -d          --debug         debug fonts-compare with logs')
        print(' -nf         --nofonts       display those languages whose fonts are not installed in your system')
        print(' -l          --lang          initialize fonts-compare with specific language')
        print(' -h          --help          display this help and exit')
        print('Learn more about fonts-compare:https://github.com/sudipshil9862/fonts-compare/blob/main/README.md')
        sys.exit()
    else:
        LOG_HANDLER_NULL = logging.NullHandler()
    GTK_VERSION =   (Gtk.get_major_version(),
                    Gtk.get_minor_version(),
                    Gtk.get_micro_version())
    app = Gtk.Application(application_id='org.github.sudipshil9862.fonts-compare')
    app.connect('activate', on_activate, cli_language)
    app.run(None)
