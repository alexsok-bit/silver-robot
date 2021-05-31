moz_version = 72.0.2
gecko_version = 0.26.0

all: bin bin/firefox bin/geckodriver bin/selenium_helper.xpi

bin:
	mkdir bin/

bin/geckodriver:
	curl -L --url "https://github.com/mozilla/geckodriver/releases/download/v$(gecko_version)/geckodriver-v$(gecko_version)-linux64.tar.gz" -o /tmp/geckodriver-v$(gecko_version)-linux64.tar.gz
	tar xfvz /tmp/geckodriver-v$(gecko_version)-linux64.tar.gz -C bin/
	chmod +x bin/geckodriver

bin/firefox:
	curl --url "https://ftp.mozilla.org/pub/firefox/releases/$(moz_version)/linux-x86_64/en-US/firefox-$(moz_version).tar.bz2" -o /tmp/firefox-$(moz_version).tar.bz2
	tar xfvj /tmp/firefox-$(moz_version).tar.bz2 -C bin/
	chmod +x bin/firefox/firefox-bin

bin/selenium_helper.xpi:
	curl -L --url "https://addons.mozilla.org/firefox/downloads/file/3784242/selenium_helper-0.0.6-fx.xpi" -o bin/selenium_helper.xpi
