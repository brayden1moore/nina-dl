#!/usr/bin/env python3
import sys, os, requests, zipfile
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, APIC, TRCK

if len(sys.argv) != 2:
    print("Usage: nina <nina_release_url>")
    sys.exit(1)

url = sys.argv[1]
release_id = url.split('/')[-1]
service_url = f'https://services.ninaprotocol.com/v1/releases/{release_id}'

resp = requests.get(service_url).json()
release = resp['release']
meta = release['metadata']['properties']
image_url = release['metadata']['image']
artist = release['publisherAccount']['displayName']
album = meta['title']

print('Downloading', album)

img_data = requests.get(image_url).content

downloads_dir = os.path.expanduser("~/Downloads")
filenames = []


for file in meta['files']:
    
    audio_url = file['uri'].replace('https://www.arweave.net/','https://node1.irys.xyz/')
    track_title = file['track_title'].replace('/','_')
    track_number = file['track']
    out_name = os.path.join(downloads_dir, f"{track_title}.mp3")

    headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity',
                'Referer': audio_url,
                'Sec-Fetch-Dest': 'audio',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-origin'
            }
    
    audio_data = requests.get(audio_url, headers=headers).content
    with open(out_name, 'wb') as f:
        f.write(audio_data)
    filenames.append(out_name)

    audio = MP3(out_name, ID3=ID3)
    try:
        audio.add_tags()
    except:
        pass

    audio.tags.add(TIT2(encoding=3, text=track_title))
    audio.tags.add(TALB(encoding=3, text=album))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img_data))
    audio.save()
    print(f"Saved {out_name}")

if len(filenames) > 1:
    album_dir = os.path.join(downloads_dir, album)
    os.makedirs(album_dir, exist_ok=True)
    for f in filenames:
        os.rename(f, os.path.join(album_dir, os.path.basename(f)))
    print(f"Saved album to folder {album_dir}")