from optparse import OptionParser
import time
from urlparse import urlparse

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, wait
import toml


parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="configuration file", default="config.toml")


# We wait until the upper right time picker is displayed, which seems to be a
# good indicator of the code being loaded. However, the requests to retrieve
# the actual data can be longer, so we give it 4 (arbitrary) extra seconds.
def wait_for_kibana(driver):
    w = wait.WebDriverWait(driver, 60)
    w.until(lambda x: x.find_element_by_class_name("navbar-timepicker-time-desc").is_displayed())
    time.sleep(4)


# Load a specific dashboard and save to file as defined by the config.
def retrieve_dashboard(driver, kibana_root, db_info):
    driver.get("{}/#/dashboard/{}".format(kibana_root, db_info["name"]))
    wait_for_kibana(driver)
    driver.save_screenshot(db_info["save_to"])


# Initialize a new driver, and load the Kibana homepage once to retrieve all
# javascript code.
def initialize_driver(kibana_root):
    driver = webdriver.Firefox()
    driver.set_window_size(1920, 1080)
    driver.get(kibana_root)
    wait_for_kibana(driver)
    return driver


# Load configuration from toml configuration file.
def load_config():
    (options, args) = parser.parse_args()
    with open(options.config) as conffile:
        config = toml.loads(conffile.read())
    kibana_root = config["kibana"]["url"]
    return kibana_root, config["dashboard"]


if __name__ == "__main__":
    kibana_root, dashboards = load_config()
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    driver = initialize_driver(kibana_root)
    for name, db_info in dashboards.items():
        start = time.time()
        retrieve_dashboard(driver, kibana_root, db_info)
        elapsed = (time.time() - start)
        print 'Saved dashboard "{}" in {:.2f}s'.format(name, elapsed)
    driver.close()
    display.stop()
