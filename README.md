# Fonts-Compare
### Fonts-Compare is a project that allows users to compare different fonts of a specific language, based on their FontWeight, FontSize, and FontStyle. The project is designed to help users choose the best font for their needs, whether they are creating a document or designing a website. The project uses the Gtk4 toolkit and requires the installation of font packages for the specific languages users wish to work with. The project is available on Fedora Copr and can also be installed by downloading the Git repository and installing the necessary dependencies.

#### Logo of fonts-compare
![fonts-compare](https://user-images.githubusercontent.com/66914502/213653980-9469d863-44dc-4765-8268-13ffa64a5906.svg)

#### Screenshots of fonts-compare UI
![fonts-compare](https://user-images.githubusercontent.com/66914502/211294452-a07102d6-71e6-42ee-b676-4f9d31b5c7db.png)
![fonts-compare-ui](https://user-images.githubusercontent.com/66914502/217479215-1f196b5d-4e1d-4363-8c33-a6a620bcfabd.png)

#### Fedora Copr Repository
You can access the Fonts-Compare Copr repository through the following link:
[fonts-compare copr link](https://copr.fedorainfracloud.org/coprs/sshil/fonts-compare/)

#### Enabling the Copr Repository
To enable the Copr repository, run the following command:

        ```
        sudo dnf copr enable sshil/fonts-compare
        ```
After enabling the Copr repository, you can install Fonts-Compare with the following command:

        ```
        sudo dnf install fonts-compare
        ```

#### If you are not using Copr, you can download the git repo and install the following packages:
        `pip3 install langtable`
        `sudo dnf install python3-langdetect`
        `sudo dnf install gtk4`
        `sudo dnf install gtk4-devel`

The code is compatible with all versions of below and above gtk4.8, including gtk4.10.

#### Here is a screenshot of Fonts-Compare UI comparing Lohit and Noto fonts for Indic languages:
[fonts-compare-lohit-vs-noto-comparison](https://sshil.fedorapeople.org/lohit-vs-noto-comparison.html)

---------------------------------------------------------------------
#### Required Font Packages
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
----------------------------------------------------------------------
#### Get languages whose Fonts are not installed in your system
    Run following commands: 

        ```
        python3 fonts_compare.py --nofonts
        ```
        or

        ```
        ./fonts_compare.py --nofonts
        ```
-----------------------------------------------------------
#### Debugging with Logs
You can enable debug mode to generate logs by running either of the following commands:

        ```
        python3 fonts_compare.py -d
        ```
        or
        ```
        python3 fonts_compare.py --debug
        ```
