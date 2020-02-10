import parameters
import lib
import os

def Main():

    current_item = 0
    lib.create_csv_file(parameters.CSV_File_PATH, parameters.Header)
    if not os.path.exists(parameters.Images_PATH):
        os.makedirs(parameters.Images_PATH)

    with open(parameters.LINKS_File_PATH) as f:
        all_links = f.read().splitlines()

    temp_browser = lib.browser_open()
    temp_browser = lib.medieval_art_login(temp_browser)

    while (current_item<=len(all_links)-1):
        print("Working on item " + str(current_item+1))
        temp_browser = lib.browser_open_url(temp_browser,all_links[current_item])
        try:
            metadata_list = lib.extract_item_metadatas(temp_browser,all_links[current_item])
            for metadata in metadata_list:
                lib.append_metadata_to_CSV(metadata, parameters.Header)
        except:
            pass
        current_item += 1
    lib.quit_browser(temp_browser)

if __name__ == '__main__':
    Main()