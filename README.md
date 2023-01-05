# Fonts-Compare
### This project is all about comparing different fonts of a particular language with respect to FontWeight, FontSize and FontStyle.

#### Logo of fonts-compare
![fonts-compare](https://user-images.githubusercontent.com/66914502/210745953-3edfef4e-fe10-4ea4-b9f6-479f4e19a128.svg)

### Fedora Copr Repository
[fonts-compare copr link](https://copr.fedorainfracloud.org/coprs/sshil/fonts-compare/)
### To enable Copr repository use command:
```
sudo dnf copr enable sshil/fonts-compare
```
```
sudo dnf install fonts-compare
```
---------------------------------------------------------------------
#### Screenshot of Fonts Compare UI and lohit vs noto fonts comparison for Indic languages
[fonts-compare-lohit-vs-noto-comparison](https://sshil.fedorapeople.org/lohit-vs-noto-comparison.html)

---------------------------------------------------------------------
#### Desktop entry file is also available
Copy fonts-compare.desktop file to /usr/share/fonts-compare after enable copr repo

---------------------------------------------------------------------
### The font packages need to be installed:
[install font packages depending upon the languages, you are going to work with]

### In Command Line type this command and Search for noto-sans-cjk fonts
```
$ sudo dnf search noto-sans-cjk
```
#### Traditional Chinese Multilingual Sans OTF font files
```
sudo dnf install google-noto-sans-cjk-hk-fonts.noarch
```
#### Japanese Multilingual Sans OTF font files for google-noto-cjk-fonts
```
sudo dnf install google-noto-sans-cjk-jp-fonts.noarch
```
#### Korean Multilingual Sans OTF font files for google-noto-cjk-fonts
```
sudo dnf install google-noto-sans-cjk-kr-fonts.noarch
```
#### Simplified Chinese Multilingual Sans OTF font files for google-noto-cjk-fonts
```
sudo dnf install google-noto-sans-cjk-sc-fonts.noarch
```
#### Traditional Chinese Multilingual Sans OTF font files for google-noto-cjk-fonts
```
sudo dnf install google-noto-sans-cjk-tc-fonts.noarch
```
#### Sans OTC font files for google-noto-cjk-fonts
```
sudo dnf install google-noto-sans-cjk-ttc-fonts.noarch
```
### [NOTE]:
- You can either install every font's packages manually or you can directly install 'ttc'
- TTC file can combine the multiple font files into a single bundle

-----------------------------------------------------------------------

### install fonts for other languages
```
sudo dnf install @fonts
```
- This will download fonts for languages like hindi(Devanagari), maratha, gujarati, odia, tamil, telegu,, arabic etc.
- if you are still facing problem with fonts then download individual packages mentioned below
----------------------------------------------------------------------

### install devanagari fonts for hindi
```
sudo dnf install google-noto-sans-devanagari-fonts.noarch
```
```
sudo dnf install google-noto-serif-devanagari-fonts.noarch
```

### install Gujarati fonts
```
sudo dnf install google-noto-sans-gujarati-fonts.noarch
```

### install Tamil fonts
```
sudo dnf install google-noto-sans-tamil-fonts.noarch
```

### install Japanese fonts
```
sudo dnf install google-noto-sans-cjk-jp-fonts.noarch
```
```
sudo dnf install google-noto-serif-jp-fonts.noarch
```

### install Arabic fonts
```
sudo dnf install google-noto-sans-arabic-fonts.noarch
```
-----------------------------------------------------------
### Debug with Logs
```
python3 fonts_compare.py -d
```
or
```
python3 fonts_compare.py --debug
```
