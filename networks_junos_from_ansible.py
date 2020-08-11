# -*- coding: utf-8 -*-
import json
import os
import sys
import re
from netaddr import *


path_to_data = r'D:\python_script\ansible\data'
path_to_result_file = r'D:\python_script\ansible\result_file.cvs'
list_files = []
error = True


def load_data_from_file(path_to_data_file):
    """
    Функция загрузки данныых из файла с результатами работы ansible.
    The function of loading data from ansible results file.
    :param path_to_data_file:
    :return:
    """
    with open(path_to_data_file, "r") as f:
        data = json.load(f)
    return data


def write_result_file(path_to_result_file, hostname, dev_int):
    """
    Функция записи результатов обработки в файл cvs.
    Function to write processing results to a cvs file.
    :param path_to_result_file:
    :param hostname:
    :param dev_int:
    :return:
    """
    if os.path.exists(path_to_result_file) is False:
        # Если файла не существует, то он будет создан
        # If the file does not exist, then it will be created.
        flag_open = "w"
    else:
        # Если файл сущствует, то он будет открыт для добаления данных.
        # If the file exists, then it will be open to add data.
        flag_open = "a"

    with open(path_to_result_file, flag_open) as f:
        f.write(hostname + '\n')
        for i in dev_int:
            f.write(i + '\n')
        f.write('\n')

def data_parsing(path_to_data, list_files):
    """
    Функция обработки данных и запись их в файл.
    The function of processing data and writing it to a file.
    :param path_to_data:
    :param list_files:
    :return:
    """
    print(list_files)
    for file in list_files:
        dev_int = ["{0};{1};{2};{3}".format("Interface", "Description", "ip_addr", "Network")]
        # для правильного извлечения hostname имя файла должен иметь формат hostname_int.json
        # for proper hostname extraction, the file name must be in the format hostname_int.json
        hostname = re.search(r'.*_int', file).group(0)[:-4]
        print(hostname)
        path_to_data_file = "{0}\{1}".format(path_to_data, file)
        data = load_data_from_file(path_to_data_file)
        interface_list = data.get("l3_interfaces")
        #print(interface_list)
        for interface in interface_list:
            description = interface.get("description")
            if description is None:
                description = "-"
            interface_name = interface.get("name")
            if type(interface.get("ipv4")) == list:
                # print("LIST")
                config_addrs = interface.get("ipv4")
                for config_addr in config_addrs:
                    net_data = list(config_addr.values())[0]
                    network = IPNetwork(net_data).cidr
                    ip_addr = IPNetwork(net_data).ip
                    dev_int.append("{0};{1};{2};{3}".format(interface_name, description, ip_addr, network))
            else:
                config_addrs = interface.get("ipv4")
                if config_addrs == None:
                    continue
                else:
                    print(hostname, config_addrs, interface_list)
                    net_data = list(config_addrs.values())[0]
                    network = IPNetwork(net_data).cidr
                    ip_addr = IPNetwork(net_data).ip
                    dev_int.append("{0};{1};{2};{3}".format(interface_name, description, ip_addr, network))

        write_result_file(path_to_result_file, hostname, dev_int)

if __name__ == "__main__":
    try:
        list_files = (os.listdir(path_to_data))
        error = False
    except Exception as e:
        print(e)

    if error is True:
        # если файла не существует, скрипт прекратит свою работу
        # if the file does not exist, the script will stop working
        sys.exit(1)
    else:
        data_parsing(path_to_data, list_files)
