from bs4 import BeautifulSoup
import requests
import urllib
import os
from os.path import expanduser, join
from bs4 import NavigableString

def make_soup(url):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    return soup

def download_files(url, directory=''):
    def download_file(url,directory=''):
        file_name = url.split('/')[-1]
        file_name = urllib.unquote(file_name)
        full_dir = join(expanduser('~'),directory)
        if not os.path.exists(full_dir):
            os.makedirs(directory)
        full_path = join(full_dir,file_name)
        print "Downloading " + file_name
        urllib.urlretrieve(url,full_path)
    
    if type(url) is list:
        for download_url in url:
            download_file(download_url,directory)
    else:
        download_file(url,directory)

def unwind_ul_tag(ul_tag, level='Root'):
    book_list = {}
    mises_base_url = 'https://mises.org'
    for item in ul_tag.children:
        if not isinstance(item,NavigableString): 
            #print "ul: " + str(item.ul != None)
            if item.ul == None:
                #print "Directory: " + str(level)
                #print "Title: " + item.a.text
                #print "URL: " + mises_base_url + item.a.get("href")
                #print "--------"
                book_list[str(level) + ": " + str(item.a.text)] = {'dir': str(level), 'title': item.a.text, 'url': mises_base_url + item.a.get("href")}
            else:
                item_level = str(level) + "/" + str(item.a.text)
                book_list[str(item.a.text) + ":"] = unwind_ul_tag(item.ul, item_level)
    
    return book_list

def get_all_book_pages(start_url):
    counter = 0
    current_url = start_url
    page_list = [start_url]
    next_page_url = get_next_page_url(current_url)
    while (next_page_url != 'end' and counter < 100):
        page_list.extend([str(next_page_url)])
        next_page_url = get_next_page_url(next_page_url)
        counter += 1
    return page_list

# Get next page function
def get_next_page_url(page_url):
    page_soup = make_soup(page_url)
    try:
        next_relative_path = page_soup.find_all("li", class_="next last")[0].a.get("href")
        next_url = "https://mises.org" + str(next_relative_path)
        return next_url
    except IndexError:
        return "end"


def get_mp3(page_urls):

    # Define a function to get mp3s from a URL and return a list
    def get_mp3s_from_url(page_url):
        all_page_mp3s = []
        page_soup = make_soup(page_url)
        all_audio = page_soup.find_all("audio")
        for audio in all_audio:
            #return audio.source.get("src")
            all_page_mp3s.append(audio.source.get("src"))
        
        return all_page_mp3s
    
    # If input is a list of URLs we need to iterate through them
    if type(page_urls) is list:
        all_mp3s = []
        for page_url in page_urls:
            all_mp3s.extend(get_mp3s_from_url(page_url))
    # Otherwise the mp3s from the one URL = all mp3s
    else:
        all_mp3s = get_mp3s_from_url(page_urls)

    return all_mp3s




#soup = make_soup('https://mises.org/library/audio-books')
#soup_book = BeautifulSoup(data_book)


all_book_pages = get_all_book_pages('https://mises.org/library/speaking-liberty-0')
print all_book_pages
all_mp3s = get_mp3(all_book_pages)
download_files(all_mp3s,'Mises/Speaking Of Liberty')
