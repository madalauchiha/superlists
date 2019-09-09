from selenium import webdriver
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
import time
import sys


class NewVisitorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # for arg in sys.argv:
        #     if 'liveserver' in arg:
        #         cls.server_url = arg.split('=')[1]
        #         return

        # cls.server_url = 'http://192.168.1.6'
        cls.server_url = 'http://10.8.2.111'
        return

        super().setUpClass()

        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()
        # pass

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):
        # 查看首页
        self.browser.get(self.server_url)

        # 首页和标题都包含“To-Do”
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # 应用邀请输入待办事项
        input_box = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(input_box.get_attribute('placeholder'),
                         'Enter a to-do item')

        # 文本框中输入“Buy peacock feathers”
        input_box.send_keys('Buy peacock feathers')

        # 她按回车后，被带到了一个新的URL
        # 这个页面的待办事项显示了“1. Buy peacock feathers”
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, r'/lists/.+')
        self.check_for_row_in_list_table('1. Buy peacock feathers')

        # 页面中又显示了一个文本框，可以输入其他待办事项
        # 他又输入了“Use peacock feathers to make a fly”
        input_box = self.browser.find_element_by_id('id_new_item')
        input_box.send_keys('Use peacock feathers to make a fly')
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # 页面再次更新，出现两个待办事项
        self.check_for_row_in_list_table('1. Buy peacock feathers')
        self.check_for_row_in_list_table('2. Use peacock feathers to make a fly')

        # 现在一个叫作弗朗西斯的新用户访问了网站
        ## 我们使用一个新浏览器会话
        ## 确保伊迪丝的信息不会从cookie中泄露出来
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # 弗朗西斯访问首页
        # 页面中看不到伊迪丝的清单
        self.browser.get(self.server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # 弗朗西斯输入一个新待办事项，新建一个清单
        # 他不像伊迪丝那样兴趣盎然
        input_box = self.browser.find_element_by_id('id_new_item')
        input_box.send_keys('Buy milk')
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # 弗朗西斯获得了他的唯一URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, r'/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # 这个页面还是没有伊迪丝的清单
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)
        self.assertIn('Buy milk', page_text)

        # 两人都很满意，去睡觉了

    def test_layout_and_styling(self):
        # 伊迪丝访问首页
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)

        # 她看到输入框完美地居中显示
        input_box = self.browser.find_element_by_id('id_new_item')
        # self.assertAlmostEqual(input_box.location['x'] + input_box.size['width'] / 2,
        #                        512,
        #                        delta=5)

        # 她新建了一个清单，发现输入狂仍然居中显示
        input_box.send_keys('testing')
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)
        input_box = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(input_box.location['x'] + input_box.size['width'] / 2,
                               512,
                               delta=5)
