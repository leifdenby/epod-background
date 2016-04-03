# EPOD background downloader

I wanted to have EPOD (Earth Science Picture of the Day) as my background image
but also have the accompanying descriptive text that's always written on the
website. So I wrote a script which runs every night using `cron` to download
the newest image and generate a background image.

## Instructions

1. Clone this repo somewhere, e.g. `/home/leif/git-repos/`

    > git clone https://github.com/leifdenby/epod-background

2. Install dependencies through pip:

    > pip install -r requirements.txt

3. Install a crontab to generate a new background every night:

    > crontab -e

    Add the following line:

        0 * * * * python /home/leif/git-repos/epod-background/dl_desktop.py¬

4. Set your window environment to use the background image downloaded to
   `/home/leif/background.jpeg`


5. Enjoy a fresh background image every morning :)


Pull requests to add more sources, fix bugs, etc welcome.
