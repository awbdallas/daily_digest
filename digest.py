#!/usr/bin/env python3

import lib.reddit as reddit
import lib.hn as hn

from configparser import ConfigParser

config_file = './resources/config.config'

def main():

    hn.get_posts()
    config = ConfigParser()
    config.read(config_file)

    r = reddit.Reddit(
        config['Main']['cid'],
        config['Main']['csecret'],
        config['Main']['password'],
        config['Main']['useragent'],
        config['Main']['username'],
    )

    print(r.reddit.user.me())

if __name__ == '__main__':
    main()

