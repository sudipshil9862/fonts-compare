import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango
from ftlangdetect import detect
import langtable
import locale

fontstyle = 'Noto Sans'
fontweight = 'Thin'
fallParam = 'fallback="false">'
fontsize = '30'
dic = {'en':{'fontweight':['Thin','Light'],
		'text':'How are you'}, 
	'bn':{'fontweight':['Bengali Thin','Bengali Regular'],
		'text':'আপনি কেমন আছেন'}, 
	'ja':{'fontweight':['CJK JP Regular','CJK JP DemiLIght'],
		'text':'元気ですか'}, 
	'ko':{'fontweight':['CJK KR Regular','CJK KR DemiLight'],
		'text':'어떻게 지내세요'}, 
	'de':{'fontweight':['Thin','Light'],
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
        self.fontbutton(self.label1, self.button1, self.hbox1, self.vbox1, 0)
        self.label2 = Gtk.Label()
        self.button2 = Gtk.FontButton.new()
        self.fontbutton(self.label2, self.button2, self.hbox2, self.vbox2, 1)
     
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
                
        result = detect(text=self.label1.get_text(), low_memory=False) #using fasttext-langdetect - returns dictionary
        detectText = result['lang']
        label3DetectLang = langtable.language_name(languageId=detectText, languageIdQuery=locale.getlocale()[0][:2])
        self.label3.set_markup('<span font="'+fontstyle+' '+dic['en']['fontweight'][0]+' '+fontsize+'"' + fallParam + label3DetectLang + '</span>')

        keycont = Gtk.EventControllerKey()
        keycont.connect('key-released', self.on_key_released)
        self.add_controller(keycont)    

        self.set_default_size(450, 450)
        self.set_child(self.vbox)
        
    def fontbutton(self, label, button, boxh, boxv, n):
        label.set_markup('<span font="'+fontstyle+' '+dic['en']['fontweight'][n]+' '+fontsize+'"' + fallParam + 'With hard work and effort, you can achieve anything' + '</span>')
        button = Gtk.FontButton.new()
        button.connect('font-set', self.label_font_change, label)
        button.set_hexpand(False)
        str = fontstyle + ' ' + dic['en']['fontweight'][n] +' '+ fontsize
        button.set_font(str)
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
        self.label1.set_markup('<span font="'+fontstyle+' '+dic[detectLang]['fontweight'][0]+' '+fontsize+'"' + fallParam + setText + '</span>')
        self.button1.set_font(fontstyle +' '+ dic[detectLang]['fontweight'][0]+' '+fontsize)
        self.label2.set_markup('<span font="'+fontstyle+dic[detectLang]['fontweight'][1]+' '+fontsize+'"' + fallParam + setText + '</span>')
        self.button2.set_font(fontstyle +' '+ dic[detectLang]['fontweight'][1]+' '+fontsize)
        
    def on_key_released(self, *_):
        result = detect(text=self.entry.get_text(), low_memory=False) #using fasttext-langdetect - returns dictionary
        detectText = result['lang']
        self.setFont(detectText,self.entry.get_text())
        label3DetectLang = langtable.language_name(languageId=detectText, languageIdQuery=locale.getlocale()[0][:2])
        self.label3.set_markup('<span font="'+fontstyle+' '+dic['en']['fontweight'][0]+' '+fontsize+'"' + fallParam + label3DetectLang + '</span>')
    
    def on_changed(self, wid):
        detectText = wid.get_active_text()
        self.setFont(detectText,dic[detectText]['text'])
        label3DetectLang = langtable.language_name(languageId=detectText, languageIdQuery=locale.getlocale()[0][:2])
        self.label3.set_markup('<span font="'+fontstyle+' '+dic['en']['fontweight'][0]+' '+fontsize+'"' + fallParam + label3DetectLang + '</span>')
    
    def langdetectfunc(self, inputtext):
        result = detect(text=inputtext, low_memory=False) #using fasttext-langdetect - returns dictionary
        detectText = result['lang']
        self.setFont(detectText,inputtext)
        label3DetectLang = langtable.language_name(languageId=detectText, languageIdQuery=locale.getlocale()[0][:2])
        self.label3.set_markup('<span font="'+fontstyle+' '+dic['en']['fontweight'][0]+' '+fontsize+'"' + fallParam + label3DetectLang + '</span>')

def on_activate(app):

    win = AppWindow(app)
    win.present()


app = Gtk.Application(application_id='org.gtk.Example')
app.connect('activate', on_activate)
app.run(None)
