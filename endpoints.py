from requests.exceptions import ConnectionError
from filelock import FileLock
import concurrent.futures
import requests
import time
import datetime as dt

class EndPoints:
    def __init__(self):
        pass

# returns any file content
    def read_file(self, filename):
        self.filename = filename
        f = open(self.filename, 'r')
        f_read = f.read().split('\n')
        f.close()
        return f_read

# writes any content to any file
    def write_file(self, filename, content):
        self.filename = filename
        self.content = content
        f = open(self.filename, 'a')
        f.write(content)
        f.close()

# returns domain/word list
    def domain_word(self):
        res = []
        obj = EndPoints()
        rd_domain = obj.read_file('domains.txt') # takes domain list from domains.txt file
        rd_word = obj.read_file('words.txt') # takes words list from words.txt file
        for domain in rd_domain:
            for word in rd_word:
                res.append(f'{domain}/{word}')
        return res

    def calc_max_iter(self, file):
        file = file
        c = 0
        for line in file:
            c += 1
        return c

# write EndPoints list to file
    def print_endpoints(self):
        obj = EndPoints()
        for i in obj.domain_word():
            obj.write_file('endpoints.txt', i+'\n')

# calculate time left
    def calcProcessTime(self, starttime, cur_iter, max_iter):
        telapsed = time.time() - starttime
        testimated = (telapsed / cur_iter) * max_iter
        finishtime = starttime + testimated
        finishtime = dt.datetime.fromtimestamp(finishtime).strftime("%H:%M:%S")
        lefttime = testimated - telapsed
        return int(lefttime), finishtime

    def separate_response(self):
        obj_endpoints = EndPoints()
        endpoint_list = obj_endpoints.read_file('endpoints.txt')
        list_23xx = 200, 201, 202, 203, 204, 205, 206, 207, 208, 218, 226, 300, 301, 302, 303, 304, 305, 306, 307, 308
        max_iter = obj_endpoints.calc_max_iter(endpoint_list)
        obj_endpoints.cur_iter = 0
        start = time.time()
        threads = 100
        open_file = open('H:\Pafession\oneshot\endpoints.txt').read().splitlines()
        urls = ['https://{}'.format(x) for x in open_file[0:]]

        def load_url(url):
            try:
                response_code = requests.head(url).status_code
                obj_endpoints.cur_iter += 1
                prstime = obj_endpoints.calcProcessTime(start, obj_endpoints.cur_iter, max_iter)
                print("\rTimeLeft: %s(s), FinishTime: %s" % prstime, end='')
                if response_code in list_23xx:
                    with FileLock("23xx.txt.lock"):
                        obj_endpoints.write_file('23xx.txt', url + '\n')
                elif response_code == 404:
                    with FileLock("404.txt.lock"):
                        obj_endpoints.write_file('404.txt', url + '\n')
                elif response_code == 429:
                    with FileLock("429.txt.lock"):
                        obj_endpoints.write_file('429.txt', url + '\n')
                else:
                    with FileLock("45xx.txt.lock"):
                        obj_endpoints.write_file('45xx.txt', url + '\n')
            except ConnectionError as e:
                with FileLock("connection_error.txt.lock"):
                    obj_endpoints.write_file('connection_error.txt', url + '\n')

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            for url in urls:
                executor.submit(load_url, url)


obj_endpoints = EndPoints()
obj_endpoints.print_endpoints()
obj_endpoints.separate_response()







