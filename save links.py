import parameters
import lib

def erase_duplicates():
    f = open(parameters.LINKS_File_PATH, "r+")
    all_links = f.read().splitlines()
    f.truncate(0)
    f.close()

    all_links_no_duplicate = list(dict.fromkeys(all_links))

    f = open(parameters.LINKS_File_PATH, "w+")
    for link in all_links_no_duplicate:
        f = open(parameters.LINKS_File_PATH, "a")
        f.write(link + "\n")


browser = lib.browser_open()
browser = lib.search_for_keyword(browser)
lib.save_links(browser)
#erase_duplicates()

