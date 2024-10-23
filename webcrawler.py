import requests
from multiprocessing import Process, Lock, Queue, Manager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse



def parse(f_list, e_set, url_process):

    url = f_list.get()
    if url in e_set:
        return
    e_set[url] = 1

    response = requests.get(url)
    response.raise_for_status()

    parsed = BeautifulSoup(response.content, 'html.parser')

    links = []
    for a_tag in parsed.find_all('a', href=True):
        if a_tag['href'] not in e_set:
            links.append(a_tag['href'])
    
    for link in links:
        f_list.put(urljoin(url_process, link))

if __name__ == "__main__":
    seed = "https://wikipedia.org"
    num_processes=100

    manager = Manager()


    f_list = manager.Queue()
    f_list.put(seed)
    e_set = manager.dict()
    processes = []
    url_process = '{}://{}'.format(urlparse(seed).scheme,
                                    urlparse(seed).netloc)

    for _ in range(num_processes):
        p = Process(target=parse, args =(f_list, e_set, url_process))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
   
    print(e_set)