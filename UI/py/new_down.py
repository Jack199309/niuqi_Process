import os
import sys
import requests
import datetime
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import time
from tqdm import tqdm


def add_to_16(bbb):
    if len(bbb) % 16:
        add = 16 - (len(bbb) % 16)
    else:
        add = 0
    bbb = bbb + (b'\0' * add)
    return bbb


class vid2(object):
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'accept': '*/*',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'referer': 'https://m.niuqixt.com/detail/v_5dd62b76575ba_Hiua99oP/3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

        self.key_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'no-cors',
            'referer': 'https://m.niuqixt.com/detail/v_5dd62b76575ba_Hiua99oP/3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }

    def get_url(self, header_url):
        res = requests.get(url=header_url, headers=self.headers, verify=False)
        return res.text

    def get_data(self, header_url):
        res = requests.get(url=header_url, headers=self.headers, verify=False)
        return res

    def get_key(self, url):
        res = requests.get(url=url, headers=self.key_headers, verify=False)
        return res


chrome = vid2()


def download(url, name):
    download_path = os.getcwd() + "\download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    # 获取第一层M3U8文件内容
    all_content = chrome.get_url(url)
    # print(all_content)
    print(all_content[0:7])
    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的链接")

    if "EXT-X-STREAM-INF" in all_content:  # 第一层
        file_line = all_content.split("\n")
        for line in file_line:
            if '.m3u8' in line:
                url = url.rsplit("/", 1)[0] + "/" + line  # 拼出第二层m3u8的URL
                all_content = requests.get(url).text

    file_line = all_content.split("\n")

    unknow = True
    key = ""
    for index, line in tqdm(list(enumerate(file_line))):  # 第二层
        # time.sleep(3)
        if not key:
            if "#EXT-X-KEY" in line:  # 找解密Key
                method_pos = line.find("METHOD")
                comma_pos = line.find(",")
                method = line[method_pos:comma_pos].split('=')[1]

                print("Decode Method：", method)

                uri_pos = line.find("URI")
                quotation_mark_pos = line.rfind('"')
                key_path = line[uri_pos:quotation_mark_pos].split('"')[1]

                # key_url = url.rsplit("/", 1)[0] + "/" + key_path  # 拼出key解密密钥URL
                # print(key_path)
                # print(key_url)
                res = chrome.get_key(key_path)
                key = res.content

                print("key：", key)

        if "EXTINF" in line:  # 找ts地址并下载
            unknow = False
            pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1]  # 拼出ts片段的URL
            res = chrome.get_data(pd_url)
            # c_fule_name = file_line[index + 1].rsplit("/", 1)[-1][0:6]
            c_fule_name = name
            if len(key):  # AES 解密
                cryptor = AES.new(key, AES.MODE_CBC, key)
                with open(os.path.join(download_path, c_fule_name + ".mp4"), 'ab') as f:

                    f.write(cryptor.decrypt(add_to_16(res.content)))
            else:
                with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                    print(len(add_to_16(res.content)))
                    f.write(add_to_16(res.content))
                    f.flush()

    if unknow:
        raise BaseException("未找到对应的下载链接")
    else:
        print("下载完成")

    # merge_file(download_path, name)


def merge_file(path, name):
    os.chdir(path)
    cmd = "copy /b * new.tmp"
    os.system(cmd)
    os.system('del /Q *.ts')
    os.system('del /Q *.mp4')
    os.rename("new.tmp", name + ".mp4")

# if __name__ == '__main__':
#     try:
#         url = input('请输入url').strip()
#         print(url)
#         name = input('请数据文件名称:').strip()
#         print(name)
#         download(url, name)
#     except IndexError:
#         print('请输入参数url和要保存的名称')
