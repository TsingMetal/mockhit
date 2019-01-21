import datetime
import logging
import os
import random
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from orm.proxy import session


class VirtualUser(object):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    date = datetime.datetime.today()
    log_dir = date.strftime('%Y%m')
    log_name = date.strftime('%Y%m%d') + '.log'
    log_file = './log/%s/%s' % (log_dir, log_name)

    if not os.path.exists('./log/%s/' % log_dir):
        os.makedirs('./log/%s/' % log_dir)

    fh = logging.FileHandler(log_file, mode='a')
    fh.setLevel(logging.INFO)
    console = logging.StreamHandler()

    formatter = logging.Formatter(
            '%(asctime)s-%(levelname)s: %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(console)

    def __init__(self, user, proxy):
        self.user = user
        self.logger.info('account:%s' % user.account)

        profile = webdriver.FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('browser.migration.version', 9001)
        profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        profile.set_preference('javascript.enabled', 'false')

        if proxy:
            self.proxy = proxy
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.http', self.proxy.ip)
            profile.set_preference('network.proxy.http_port', self.proxy.port)
            profile.set_preference('network.proxy.ssl', self.proxy.ip)
            profile.set_preference('network.proxy.ssl_port', self.proxy.port) 
            self.logger.info('proxy ip:%s country:%s'
                    % (proxy.ip, proxy.country))
        else:
            self.logger.info('without proxy')

        profile.update_preferences()

        self.browser = webdriver.Firefox(profile)
        self.browser.implicitly_wait(30)
        
    def login(self):
        url = 'https://alibaba.com'
        try:
            self.browser.get(url)
            sign_in_link = \
                    self.browser.find_element_by_link_text('Sign In')
            if self.proxy:
                self._update_proxy(1)
            sign_in_link.click()
            self.logger.info('sign in link clicked')
        except Exception as e:
            if self.proxy:
                self.logger.info('connect failed with %s' % self.proxy.ip)
                self._update_proxy(0)
            else:
                self.logger.info('connect failed without proxy')
            self.quit()
            return False

        try:
            self.browser.switch_to.frame('alibaba-login-box')
            self.logger.info('switch to login box OK')
        except:
            self.logger.info('switch to login box FAIL')
            self.quit()
            return False

        id_box = self.browser.find_element_by_id('fm-login-id')
        id_box.send_keys(self.user.account)
        time.sleep(1)
        passwd_box = self.browser.find_element_by_id('fm-login-password')
        passwd_box.send_keys(self.user.passwd)
        sumit_btn = self.browser.find_element_by_id('fm-login-submit')
        sumit_btn.click()
        self.logger.info('login button clicked')
        self.browser.switch_to.default_content()
        
        try:
            search_box = self.browser.find_element_by_class_name(
                    'ui-searchbar-keyword')
            if self.proxy:
                self.logger.info('%s logged in with %s'
                        % (self.user.account, self.proxy.ip))
            else:
                self.logger.info('%s logged in' % self.user.account)
        except:
            self.logger.info('log in FAIL')
            self.quit()
            return False

        return True

    def _update_proxy(self, is_valid):
        try:
            self.proxy.is_valid = is_valid
            date_form = '%Y-%m-%d'
            date = datetime.datetime.today().strftime(date_form)
            self.proxy.update_date = date
            session.add(self.proxy)
            session.commit()
        except:
            session.rollback()
            self.quit()

    def visit_random(self):
        try:
            search_box = self.browser.find_element_by_class_name(
                    'ui-searchbar-keyword')
            search_box.clear()
            search_box.send_keys('eyelashes')
            time.sleep(1)
            btn = self.browser.find_element_by_class_name(
                    'ui-searchbar-submit')
            btn.click()
            self.logger.info('key word searched')
        except:
            self.logger.info('connection broken')

        try:
            links = self.browser.find_elements_by_class_name(
                        'util-valign-inner')
            links[random.choice((0, 1, 2, 3))].click()
            self.logger.info('random link clicked')
        except:
            self.logger.info('visit random FAIL')

    def visit_target(self, target_url):
        self.browser.get(target_url)
        try:
            contact_sup = self.browser.find_element_by_link_text(
                    'Contact Supplier')
            contact_sup.click()
            self.logger.info('Contact Supplier clicked')
        except:
            self.logger.info('connection broken')
            return

        try:
            textarea = self.browser.find_element_by_id('inquiry-content')
            if self.proxy:
                mail_template = '''
this is scam mail sent from a bot.
account: %s
proxy ip: %s
country: %s
                '''
                textarea.send_keys(mail_template 
                        % (self.user.account,
                            self.proxy.ip,
                            self.proxy.country))
            else:
                mail_template = 'this is scam mail sent from a bot'
                textarea.send_keys(mail_template % self.user.account)
            time.sleep(1)
            send_btn = self.browser.find_element_by_class_name(
                    'ui2-button')
            send_btn.click()
            self.logger.info('send mail button clicked')
        except:
            self.logger.info('connection broken')

    def quit(self):
        self.browser.quit()


if __name__ == '__main__':
    from orm.proxy import Proxy
    query = session.query(Proxy).all()
    proxy = query[random.choice(range(20))]
    print(proxy)

    class User:
        def __init__(self, 
                     account='tsingmetal02@gmail.com',
                     passwd='7630.alibaba'):
            self.account = account
            self.passwd = passwd

    user = User()

    vuser = VirtualUser(user, proxy)
    vuser.login()
    vuser.visit_random()
    url = 'https://www.alibaba.com/product-detail/Wholesale-Private-Label-Natural-3D-Mink_60746199247.html?spm=a2700.8443322.0.0.74713e5fkOlA2x'
    vuser.visit_target(url)
    vuser.quit()
