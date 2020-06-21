from selenium import webdriver
import time
from selenium.common.exceptions import StaleElementReferenceException

url = 'https://www.douyu.com/directory'

# 打开一个chrome浏览器
driver = webdriver.Chrome('D:\software\Code\chromedriver.exe')

driver.get(url)

part_kes = ('part_name', 'hot', 'room_num')
room_keys = ('part', 'anchor', 'room_name', 'hot')
room_num = 0
max_hot = 0
max_room_hot = 0


# 获得板块名

def getPartName():
    dict_part = []
    for i in range(3, 13, 1):
        try:
            item = driver.find_elements_by_xpath('//section/div[{}]/div/h4'.format(i))[0]
            print("{}\n---------------".format(item.text))
            openPart(i, dict_part)
        except StaleElementReferenceException as msg:
            exceptPrint(msg, 'getPartName')
            item = driver.find_elements_by_xpath('//section/div[{}]/div/h4'.format(i))[0]
            print("{}\n---------------".format(item.text))
            openPart(i, dict_part)
    getPartMax(dict_part)


# 打开每一个板块
def openPart(i, dict_part):
    global max_hot
    xpath_str = '//section/div[{}]/ul/li/a'.format(i)
    part_links = driver.find_elements_by_xpath(xpath_str)
    for j in range(1, len(part_links), 1):
        time.sleep(3)
        if len(driver.find_elements_by_xpath('//section/div[{}]/ul/li[{}]/a/strong'.format(i, j))):

            link = driver.find_elements_by_xpath('//section/div[{}]/ul/li[{}]/a'.format(i, j))[0]
            item = driver.find_elements_by_xpath('//section/div[{}]/ul/li[{}]/a/strong'.format(i, j))[0]
            item_hot = driver.find_elements_by_xpath('//section/div[{}]/ul/li[{}]/a/div/span'
                                                     .format(i, j))[0]
            print("\t游戏名：{}".format(item.text))
            print("\t游戏总热度：{}".format(item_hot.text))
            # 计算最高热度
            hot_data = hotTransfer(item_hot.text)
            if hot_data > max_hot:
                max_hot = hot_data
                # print(max_hot)
        else:
            break

        try:
            # 进入板块
            link.click()
            # 切换到新窗口
            switchWindow()
            # 获取改板块主播信息
            num = getPartInfo(room_num)
            # 关闭爬取完毕的标签
            driver.close()
            # 切换到初始标签
            switchWindow()
            values = (item.text, hot_data, num)
            dict_part.append({k: v for k, v in zip(part_kes, values)})
        except StaleElementReferenceException as msg:
            exceptPrint(msg, 'openPart')
            item.click()
            switchWindow()
            num = getPartInfo(room_num)
            driver.close()
            switchWindow()
            values = (item.text, hot_data, num)
            dict_part.append({k: v for k, v in zip(part_kes, values)})
    print('*************************************')


def getPartInfo(room_num):
    global max_room_hot
    dict_room = []
    # 下一页按钮
    next_btn = driver.find_elements_by_xpath('//section[2]/div[2]/div/ul/li/a')
    next_len = len(next_btn)
    # 获取总页数
    if next_len != 0:
        page_len = int(next_btn[len(next_btn) - 1].text) if int(next_btn[len(next_btn) - 1].text) != 0 else 1
        next_btn = driver.find_elements_by_xpath('//section[2]/div[2]/div/ul/li[{}]/span'.format(next_len + 2))[0]
    else:
        page_len = 1
    ALL_PAGE = page_len
    while page_len:
        li = 1
        try:
            # 主播信息下一页
            print("*************************第{}页*************************".format(ALL_PAGE - page_len + 1))
            time.sleep(1)
            while len(driver.find_elements_by_xpath(
                    '//section[2]/div[2]/ul/li[{}]/div/a[1]/div[2]/div[1]/h3'.format(li))):
                room_name = '//section[2]/div[2]/ul/li[{}]/div/a[1]/div[2]/div[1]/h3'.format(li)
                room_person = '//section[2]/div[2]/ul/li[{}]/div/a[1]/div[2]/div[2]/h2'.format(li)
                room_hot = '//section[2]/div[2]/ul/li[{}]/div/a[1]/div[2]/div[2]/span'.format(li)
                room_game = '//section[2]/div[2]/ul/li[1]/div/a[1]/div[2]/div[1]/span'.format(li)
                try:
                    room_name = driver.find_elements_by_xpath(room_name)[0].text
                    room_anchor = driver.find_elements_by_xpath(room_person)[0].text
                    room_hot = driver.find_elements_by_xpath(room_hot)[0].text
                    room_part = driver.find_elements_by_xpath(room_game)[0].text
                except StaleElementReferenceException as msg:
                    room_name = driver.find_elements_by_xpath(room_name)[0].text
                    room_anchor = driver.find_elements_by_xpath(room_person)[0].text
                    room_hot = driver.find_elements_by_xpath(room_hot)[0].text
                    room_part = driver.find_elements_by_xpath(room_game)[0].text
                hot_data = hotTransfer(room_hot)
                if hot_data > max_room_hot:
                    max_room_hot = hot_data
                print("所属板块：{}".format(room_part))
                print("房间名：{}".format(room_name))
                print("主播：{}".format(room_anchor))
                print("热度：{}".format(room_hot))
                print()
                values = (room_part, room_anchor, room_name, hot_data)
                dict_room.append({k: v for k, v in zip(room_keys, values)})
                li += 1
        except StaleElementReferenceException as msg:
            exceptPrint(msg, 'getPartInfoOut')
            # 主播信息下一页
            print("*************************第{}页*************************".format(ALL_PAGE - page_len + 1))
            time.sleep(1)
        if next_len != 0:
            next_btn.click()
        room_num += li
        page_len -= 1
    getRoomMax(dict_room)
    dict_room.clear()
    max_room_hot = 0
    return room_num


# 切换窗口
def switchWindow():
    win = driver.window_handles
    driver.switch_to.window(win[-1])


def exceptPrint(msg, where):
    print("查找异常元素{}\nfrom>>>{}".format(msg, where))
    print("重新获取元素")
    webdriver.Chrome.refresh(driver)
    time.sleep(1)


def hotTransfer(hot):
    hot_len = len(hot) - 1
    hot_data = hot[:hot_len]
    if hot[hot_len] == '万':
        return float(hot_data) * 10000
    elif hot_len == 0:
        return 0
    else:
        return float(hot_data)


def getPartMax(dict):
    for item in dict:
        if float(item['hot']) == max_hot:
            print("热度最高的板块为：")
            print("板块名：{}\n热度：{}\n直播房间数：{}".format(item['part_name'], item['hot'], item['room_num']))
    print("\n\n")

def getRoomMax(dict):
    for item in dict:
        if float(item['hot']) == max_room_hot:
            print("热度最高的主播为：")
            print("板块名：{}\n直播房间名：{}\n主播：{}\n热度：{}".
                  format(item['part'], item['room_name'], item['anchor'], item['hot']))
    print("\n\n")



if __name__ == "__main__":
    getPartName()
