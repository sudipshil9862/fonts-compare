# fonts-compare
`fonts-compare` is a GTK4-based visual font comparison tool that helps you **explore, analyze, and choose the best fonts** for your specific language needs based on their FontWeight, FontSize, and FontStyle. Whether you’re designing a multilingual UI, creating a document, or just curious about typography in your language, this tool has you covered. The project is available on Fedora, epel and can also be installed by downloading the Git repository and installing the necessary dependencies.

### NOTE: `fonts-compare` package is compatible with all GTK versions

### Logo of fonts-compare
![fonts-compare](https://user-images.githubusercontent.com/66914502/213653980-9469d863-44dc-4765-8268-13ffa64a5906.svg)

### Screenshots of fonts-compare UI
![fonts-compare](https://github.com/sudipshil9862/fonts-compare/assets/66914502/f8d5da8d-9461-401f-bac0-2500fec9ca4c)
![fonts-compare-ui](https://github.com/sudipshil9862/fonts-compare/assets/66914502/cc65f007-64e5-4972-bd45-ac995f388164)

### ✨ Key Highlights

-  **Pango Sample Text:** Get meaningful sample sentences with a checkbox—no need to come up with test text on your own.
-  **Language-Aware Fallback:** Mix scripts in your text? Enable fallback to render all characters correctly.
-  **Font Version at a Glance:** Shows live version info as you switch fonts or languages.
-  **Show Font Style:** Toggle between just family names or detailed family + style.
-  **Editable Labels:** Customize your test sentences through a simple edit dialog.
- ️ **Auto Language Detection:** Know what language your test text is in—great for multilingual debugging.
-  **Smart Text Wrapping:** Automatically adjusts long sentences for better readability and layout
-  **Dark Mode Support:** Respects your system theme, or toggle it manually if you're team dark mode.
- ℹ️ **About Section:** Dive deeper into the purpose and background of fonts-compare with just a click.


### Fedora Users
For fedora users, you can install fonts-compare with the following command:

        ```
        sudo dnf install fonts-compare
        ```

### If you are not using fedora, then you can download the git repo and install the following packages:
        ```
        git clone https://github.com/sudipshil9862/fonts-compare.git`
        ```        
        `pip3 install langtable`
        `sudo dnf install python3-langdetect`
        `sudo dnf install gtk4`
        `sudo dnf install gtk4-devel`
        `sudo dnf install python3-freetype`
        `sudo dnf install freetype-devel`

make sure you have pip updated `pip install --upgrade pip` and python devel is installed `sudo dnf install python3-devel`


### Here is a screenshot of fonts-compare UI comparing Lohit and Noto fonts for Indic languages:
[fonts-compare-lohit-vs-noto-comparison](https://sshil.fedorapeople.org/lohit-vs-noto-comparison.html)

---------------------------------------------------------------------
### Required Font Packages
[Please install font packages based on the languages you need to use]

- You can install the 'ttc' package, which combines multiple font files into a single bundle, instead of manually installing each font package
- To search for language-specific font packages, use the command:
        ```
        sudo dnf search any_language_name
        ```
- You can download fonts for various languages, such as Hindi (Devanagari), Marathi, Gujarati, Odia, Tamil, Telugu, Arabic, and more, by running the following command:

        ```
        sudo dnf install @fonts
        ```
---------------------------------------------------------------------
### Now, let's explore some of the features that make fonts-compare unique:

`Pango sample text:` If you prefer not to come up with your own sentence for testing, fonts-compare provides a "pango sample text" checkbox that generates sample text for easy font comparison.

`Wrap labels:` When dealing with longer sentences that don't fit within the screen, fonts-compare automatically wraps labels and breaks lines into manageable pieces for a proper view. However, the tool also has the capability to fit sentences automatically.

`Fallback:` Occasionally, you may have text with letters from different languages. To ensure all letters are displayed correctly, simply enable the "fallback" checkbox. This feature allows you to view all letters in their proper forms, regardless of the font.

`Fontversion:` Get fontversion for any font that is selected in fontbutton. changing font or changing language also update the update the fontversion in runtime

`Show style:` by default only family is displayed and selected for a font. But if user want to use family-style of a font, user can select the showstyle check box, it'll make displaying the style along with family

`Edit labels:` If you wish to customize the text of the labels or the pango sample text, use the "edit labels" option in the hamburger icon. This feature opens a dialog box where you can easily modify the text according to your preferences.

`Detect language from text:` Inside the "edit labels" dialog box, you'll find a section that identifies the language in which the text was written. This language detection feature helps you gain insights into the text's origin.

`Dark theme:` fonts-compare seamlessly adapts to your system's theme, be it dark or light. If your system is set to a dark theme, the tool will automatically start in dark mode. However, if you prefer, you can enable the dark theme manually by selecting the "dark theme" option in the hamburger icon.

`About fonts-compare:` To learn more about fonts-compare, its purpose, and additional resources, check out the "about" section. There, you'll find links to relevant information that will deepen your understanding of the tool.

---------------------------------------------------------------
### Open fonts-compare with specific language
        ```
        python3 fonts_compare.py --lang <lang_input>
        ```
        or
        ```
        ./fonts_compare.py --lang <lang_input>
        ```
---------------------------------------------------------------
### open fonts-compare with locale language
##### [NOTE: input language must be supported by fontconfig]
##### Below command will open fonts-compare with <lang_locale>
        ```
        LC_ALL=<lang_locale>.utf8 ./fonts_compare.py
        ```
##### Below command will open fonts-compare with <lang>
        ```
	    LC_ALL=<lang_locale>.utf8 ./run.sh -l <lang>
	    ```
#### [NOTE: if your locale is <lang> and you are directly running ./fonts_compare.py then it will initialize with <lang>
---------------------------------------------------------------
### Open fonts-compare with Pre-Filled Text
    You can launch fonts-compare with a specific text pre-filled using the --text argument.
        ```
        python3 fonts_compare.py --text "বাংলা ফন্ট পরীক্ষা" "Test fonts in English"
        ```
        or
        ```
        ./fonts_compare.py --text "বাংলা ফন্ট পরীক্ষা" "Test fonts in English"
        ```
---------------------------------------------------------------
### Get languages whose Fonts are not installed in your system
    Run following commands: 

        ```
        python3 fonts_compare.py --nofonts
        ```
        or

        ```
        ./fonts_compare.py --nofonts
        ```
---------------------------------------------------------------
### Debugging with Logs
You can enable debug mode to generate logs by running either of the following commands:

        ```
        python3 fonts_compare.py -d
        ```
        or
        ```
        python3 fonts_compare.py --debug
        ```
--------------------------------------------------------------
### Do you need help ?
        ```
        python3 fonts_compare.py --help
        ```
        ```
        ./fonts_compare.py --help
        ```
