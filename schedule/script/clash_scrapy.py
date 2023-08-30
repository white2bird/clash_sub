# https://clashnode.com/wp-content/uploads/2023/08/20230810.yaml
# https://nodefree.org/dy/2023/08/20230810.yaml
import requests
import yaml
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}


def aggregate_clash_subscriptions(subscription_links):
    proxies_name = set()

    aggregated_config = {
        "proxies": [],
        "rules": [],
        "proxy-groups": []
        # 其他配置项...
    }

    global_rules = set()

    for link in subscription_links:
        url_res = requests.get(link, headers=headers)

        subscription_config = yaml.safe_load(url_res.text)

        new_proxies_list = []
        try:
            proxies = subscription_config.get("proxies", [])
            for proxy in proxies:
                if proxy['type'] is None or proxy['type'] == 'vless':
                    continue
                name = proxy['name']
                if name in proxies_name:
                    continue
                new_proxies_list.append(proxy)
                proxies_name.add(name)

            aggregated_config["proxies"].extend(new_proxies_list)

            origin_proxy_groups = subscription_config.get("proxy-groups", [])
            for origin_proxy_group in origin_proxy_groups:
                temp_proxies = origin_proxy_group['proxies']
                if temp_proxies is not None:
                    for item in temp_proxies:
                        if item not in proxies_name:
                            temp_proxies.remove(item)

            aggregated_config["proxy-groups"].extend(origin_proxy_groups)

            new_rules = []
            origin_rules = subscription_config.get("rules", [])
            for rule_str in origin_rules:
                rules_res = rule_str.split(',')
                if len(rules_res) == 3:
                    domain_name = rules_res[1]
                    if domain_name in global_rules:
                        continue
                    global_rules.add(domain_name)
                    new_rules.append(rule_str)
            aggregated_config["rules"].extend(new_rules)
        except Exception as e:
            logger.error(e)
    return aggregated_config


if __name__ == "__main__":
    # subscription_links = ["https://clashnode.com/wp-content/uploads/2023/08/20230818.yaml",
    #                       "https://nodefree.org/dy/2023/08/20230818.yaml"]  # 替换为实际的订阅链接
    # aggregated_config = aggregate_clash_subscriptions(subscription_links)
    #
    # # 将合并后的配置写入一个文件
    # with open("../merged_config20230818.yaml", 'w', encoding="utf-8") as file:
    #     with open("../proxy_head.txt", 'r') as head_file:
    #         lines = head_file.readlines()
    #         for line in lines:
    #             file.write(line)
    #
    #     yaml.dump(aggregated_config, file, default_flow_style=False, allow_unicode=True)
    classnodeUrl = 'https://clashnode.com/'
    nodefreeUrl = 'https://nodefree.org/'
    session = requests.session()
    res = session.get(classnodeUrl)
    soup = BeautifulSoup(res.text, 'html.parser')

    # print(res.text)
    # 使用选择器查找具有 class="item-content" 的元素
    item_content_elements = soup.select('h2[cp-post-title]')

    # 打印找到的元素内容
    for element in item_content_elements:
        next_url = element.a['href']
        inner_res = session.get(next_url)
        # print(inner_res.text)

        inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
        section_list = inner_soup.select('p')
        for section in section_list:
            if section.string:
                pass


        break
