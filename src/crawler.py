import os
import json
import time

from selenium.webdriver.common.by import By

from _datetime import datetime
now = datetime.now()


class AlbaCrawler:

    def __init__(self, areacode):
        self.AREACODE = areacode

    def save_json(self, result_list):

        json_list = []
        json_list_areacode = []

        dir_path = f"{os.getcwd()}/result"
        for (root, directories, files) in os.walk(dir_path):
            for file in files:
                if '.json' in file:
                    file_path = os.path.join(root, file)
                    json_list.append(file_path)

        for j in json_list:
            if self.AREACODE == j[-28:-25] or self.AREACODE == j[-27:-25]:
                json_list_areacode.append(j)

        if len(json_list_areacode) > 0:
            latest_json_path = json_list_areacode[-1]
            with open(latest_json_path) as latest:
                latest_data = json.load(latest)

            with open(f"result/{self.AREACODE}_{now.strftime('%Y-%m-%d %H:%M:%S')}.json", "w",
                      encoding="utf-8") as json_file:
                json.dump(latest_data + result_list, json_file, indent='\t', ensure_ascii=False)
        else:
            with open(f"result/{self.AREACODE}_{now.strftime('%Y-%m-%d %H:%M:%S')}.json", "w",
                      encoding="utf-8") as json_file:
                json.dump(result_list, json_file, indent='\t', ensure_ascii=False)

    def extract_data(self, url, driver):

        driver.get(url)

        login_required = True
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
        except:
            login_required = False

        if login_required:
            return "login required"

        title = driver.find_element(By.CSS_SELECTOR, "h2.detail-content__title").text
        company = driver.find_element(By.CSS_SELECTOR, "strong.detail-content__tag-branch").text
        post_date = driver.find_element(By.CSS_SELECTOR, "div#DetailView div.detail-regist__date > em:first-child").text

        n = 3
        while True:
            dl = driver.find_element(By.CSS_SELECTOR, f"div#InfoWork dl:nth-child({n})").text
            address = driver.find_element(By.CSS_SELECTOR, f"div#InfoWork dl:nth-child({n - 1})").text.replace("근무지주소",
                                                                                                               "").strip()
            if "동정보" in dl:
                break
            else:
                n += 1

        raw_local_info = dl.replace("동정보", "").strip()
        local_info = raw_local_info.split(" ")
        # province = local_info[0].strip() -> ex) 경기
        try:
            city = local_info[1].strip()
        except:
            city = "X"
        try:
            dong = local_info[2].strip()
        except:
            dong = "X"

        sex = driver.find_element(By.CSS_SELECTOR,
                                  "div.detail-content__condition-list:first-child > dl:nth-child(2) > dd").text
        age = driver.find_element(By.CSS_SELECTOR,
                                  "div.detail-content__condition-list:first-child > dl:nth-child(3) > dd").text.replace(
            '\n', ' / ')
        education = driver.find_element(By.CSS_SELECTOR,
                                        "div.detail-content__condition-list:first-child > dl:nth-child(4) > dd").text
        occupation = driver.find_element(By.CSS_SELECTOR,
                                         "div.detail-content__condition-list:first-child > dl:nth-child(5) li").text
        jop_type = driver.find_element(By.CSS_SELECTOR,
                                       "div.detail-content__condition-list:first-child > dl:nth-child(6) > dd").text
        num_of_recruits = driver.find_element(By.CSS_SELECTOR,
                                              "div.detail-content__condition-list:first-child > dl:nth-child(7) > dd").text
        try:
            prefer_treat = driver.find_element(By.CSS_SELECTOR,
                                               "div.detail-content__condition-list:first-child > dl:nth-child(8) > dd").text
        except:
            prefer_treat = "X"
        try:
            pay_type = driver.find_element(By.CSS_SELECTOR,
                                           "div.detail-content__condition-list:nth-child(2) > dl:nth-child(2) > dd > p > i").text.strip()
        except:
            pay_type = "X"
        try:
            pay_money = driver.find_element(By.CSS_SELECTOR,
                                        "div.detail-content__condition-list:nth-child(2) > dl:nth-child(2) > dd > p > strong").text + "원".strip()
        except:
            pay_money = "X"
        emp_period = driver.find_element(By.CSS_SELECTOR,
                                         "div.detail-content__condition-list:nth-child(2) > dl:nth-child(3) > dd").text
        working_day = driver.find_element(By.CSS_SELECTOR,
                                          "div.detail-content__condition-list:nth-child(2) > dl:nth-child(4) > dd").text
        working_time = driver.find_element(By.CSS_SELECTOR,
                                           "div.detail-content__condition-list:nth-child(2) > dl:nth-child(5)").text.replace(
            "근무시간", "").strip().replace("\n", " / ")

        result_json = {
            "title": title,
            "company": company,
            "address": address,
            # "province": province,
            "city": city,
            "dong": dong,
            "postDate": post_date,
            "sex": sex,
            "age": age,
            "education": education,
            "occupation": occupation,
            "jobType": jop_type,
            "numberOfRecruits": num_of_recruits,
            "preferential": prefer_treat,
            "payType": pay_type,
            "payMoney": pay_money,
            "employmentPeriod": emp_period,
            "workingDay": working_day,
            "workingTime": working_time,
            "url": url
        }

        return result_json

    def manage_extract(self, driver, url_dict_list, num_of_item):
        result_list = []
        n = 1
        for i in url_dict_list:

            if i["scraped"] == "False":
                try:
                    result_json = self.extract_data(i["url"], driver)
                    if result_json == "login required":
                        i["scraped"] = "login required"
                        print(f"No.{n} scrap failed(login required)")
                    else:
                        result_list.append(result_json)
                        # scrap된 url의 scraped를 True로 변환
                        i["scraped"] = "True"
                        print(f"No.{n} scraped successfully")

                    time.sleep(2)

                except:
                    print(f"No.{n} scrap failed(error)")

            elif i["scraped"] == "login required":
                print(f"No.{n} pass(login required)")

            else:
                print(f"No.{n} pass(scraped)")

            n += 1

            if n == num_of_item+1:
                break

        driver.quit()

        self.save_json(result_list)

        return url_dict_list
