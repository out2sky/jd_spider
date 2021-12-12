import requests
from bs4 import BeautifulSoup
import xlwt

# 表格标题
TITLE_LABEL = ['商品编号', '商品名称', '图片路径', '价格', '商家', '商品详情地址']
GOOD_LABEL = ['no', 'name', 'img_url', 'price', 'shop', 'detail_addr']


class Excel:
    # 表格列数
    TABLE_COL = len(TITLE_LABEL)
    # 当前行数
    _current_row = 1

    # 初始化，创建文件及写入title
    def __init__(self, sheet_name='sheet1'):
        self.write_work = xlwt.Workbook(encoding='ascii')
        self.write_sheet = self.write_work.add_sheet(sheet_name)
        for item in range(len(TITLE_LABEL)):
            self.write_sheet.write(0, item, label=TITLE_LABEL[item])

    # 写入内容
    def write_content(self, content):
        for item in range(self.TABLE_COL):
            self.write_sheet.write(self._current_row, item, label=content[GOOD_LABEL[item]])
        # 插入完一条记录后，换行
        self._current_row += 1

    # 保存文件
    def save_file(self, file_url='./dj_data.xls'):
        try:
            self.write_work.save(file_url)
            print("文件保存成功！文件路径为：" + file_url)
        except IOError:
            print("文件保存失败！")


class Goods:
    # 初始化方法
    def __init__(self, li_info):
        self.li_info = li_info
        self.good_info_dic = {}

    def find_attr(self, attr):
        try:
            if attr == GOOD_LABEL[0]:
                # 商品编号
                result = self.li_info['data-sku']
            elif attr == GOOD_LABEL[1]:
                # 商品名称
                result = self.li_info.find(class_='p-name p-name-type-2').find('em').get_text()
            elif attr == GOOD_LABEL[2]:
                # 图片路径
                # result = self.li_info.find(class_='p-img').find('img')['src']
                result = 'http:' + self.li_info.find(class_='p-img').find('img')['data-lazy-img']
            elif attr == GOOD_LABEL[3]:
                # 价格
                result = self.li_info.find(class_='p-price').find('i').get_text()
            elif attr == GOOD_LABEL[4]:
                # 商家
                result = self.li_info.find(class_='p-shop').find('a').get_text()
            elif attr == GOOD_LABEL[5]:
                # 商品详情地址
                result = 'http:' + self.li_info.find(class_='p-name p-name-type-2').find('a')['href']
        except AttributeError:
            result = '无'
        self.good_info_dic.setdefault(attr, result)

    # 添加商品信息
    def add_good_info(self):
        for item in GOOD_LABEL:
            self.find_attr(item)

    # 获取产品列表
    def get_good(self):
        return self.good_info_dic


def get_html(url, currentPage, pageSize):
    # 模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    print("--> 正在获取网站第 " + str(currentPage) + "页信息")
    if currentPage != 1:
        url = url + '&page=' + str(currentPage) + '&s=' + str(pageSize) + '&click=0'

    response = requests.get(url, headers=headers)  # 请求访问网站
    if response.status_code == 200:
        html = response.text  # 获取网页源码
        return html  # 返回网页源码
    else:
        print("获取网站信息失败！")


if __name__ == '__main__':
    # 创建文件
    excel = Excel()
    # 搜索关键字
    keyword = 'ssd'
    # 搜索地址
    search_url = 'https://search.jd.com/Search?keyword=' + keyword + '&enc=utf-8'
    total = input('请输入需要爬取页数: ')
    page = {
        'total': 0,  # 总页数
        'currentPage': 1,  # 当前页数
        'pageSize': 0  # 每页显示多少条
    }
    if not total.isdigit():
        print("非法字符，程序退出！")
        exit(0)

    page['total'] = eval(total)
    for i in range(page['total']):
        # 初始化BeautifulSoup库,并设置解析器
        soup = BeautifulSoup(get_html(search_url, page['currentPage'], page['currentPage'] * page['pageSize']), 'lxml')
        # 商品列表
        goods_list = soup.find_all('li', class_='gl-item')
        print("分析到第" + str(page['currentPage']) + '页共有' + str(len(goods_list)) + '条商品信息')
        for li in goods_list:  # 遍历父节点
            goods = Goods(li)
            # 添加信息
            goods.add_good_info()
            # 获取信息
            good_info = goods.get_good()
            # 写入excel
            excel.write_content(good_info)

        page['currentPage'] = page['currentPage'] + 1
        page['pageSize'] = len(goods_list) * page['currentPage']

    excel.save_file('jd_data.xls')
