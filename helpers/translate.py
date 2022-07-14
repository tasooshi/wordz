#!/usr/bin/env python3

import argparse
import unidecode

from google.cloud import translate_v2


def normalize(value):
    return unidecode.unidecode(value)


def entry_point():
    parser = argparse.ArgumentParser(description='Translation script')
    parser.add_argument('-s', '--source', required=True, help=f'Source file (English keywords')
    parser.add_argument('-l', '--language', required=True, help='Language code to translate to')
    args = parser.parse_args()

    translate_client = translate_v2.Client()

    with open(args.source, 'r') as fil:
        inp = fil.readlines()
        while inp:
            segment = [lin.strip() for lin in inp[:128]]
            result = translate_client.translate(segment, source_language='en', target_language=args.language)
            words = '\n'.join([normalize(itm['translatedText']) for itm in result])
            del(inp[:128])
            print(words)


if __name__ == '__main__':
    entry_point()
