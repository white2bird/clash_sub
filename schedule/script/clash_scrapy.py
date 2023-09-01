# https://clashnode.com/wp-content/uploads/2023/08/20230810.yaml
# https://nodefree.org/dy/2023/08/20230810.yaml
import requests
import logging
# from ruamel.yaml import YAML
from bs4 import BeautifulSoup
import yaml

logger = logging.getLogger()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}


def construct_str(loader, node):
    value = loader.construct_scalar(node)
    print('----------------value--------------')
    print(str(value))
    return str(value)


# 注册自定义构造函数
yaml.add_constructor('!<str>', construct_str)
yaml.add_constructor('!<str>', construct_str)

def aggregate_clash_subscriptions(subscription_links, type_mobile="mobile"):
    proxies_name = list()
    aggregated_config = {
        "proxies": [],
        "rules": [],
        "proxy-groups": []
        # 其他配置项...
    }



    global_rules = list()

    for link in subscription_links:
        url_res = requests.get(link, headers=headers)
        no_else_text = url_res.text.replace('!<str>', '')

        subscription_config = None
        new_proxies_list = []
        try:
            subscription_config = yaml.safe_load(no_else_text)
            proxies = subscription_config.get("proxies", [])
            for proxy in proxies:
                if proxy['type'] is None or proxy['type'] == 'vless':
                    continue
                if type_mobile != "mobile" and proxy['type'] == 'ss':
                    # 是电脑
                    continue
                name = proxy['name']
                if "中国" in name:
                    continue
                if name in proxies_name:
                    continue
                new_proxies_list.append(proxy)
                proxies_name.append(name)

            aggregated_config["proxies"].extend(new_proxies_list)

            origin_proxy_groups = subscription_config.get("proxy-groups", [])
            new_proxy_groups = []
            for origin_proxy_group in origin_proxy_groups:
                proxy_info = dict()
                proxy_info['name'] = origin_proxy_group['name']
                proxy_info['type'] = origin_proxy_group['type']
                proxies = []
                temp_proxies = origin_proxy_group['proxies']
                if temp_proxies is not None:
                    to_delete_name = []
                    for item in temp_proxies:
                        if str(item).lower() == "DIRECT".lower() or str(item).lower() == "REJECT".lower() or "选择" in item:
                            continue
                        if "中国" in str(item):
                            temp_proxies.remove(item)
                            continue
                        if item not in proxies_name:
                            continue
                        else:
                            proxies.append(item)
                            to_delete_name.append(item)
                    if to_delete_name and len(to_delete_name) > 0:
                        for name in to_delete_name:
                            proxies_name.remove(name)
                proxy_info['proxies'] = proxies
                if len(proxies) > 0:
                    new_proxy_groups.append(proxy_info)

            aggregated_config["proxy-groups"].extend(new_proxy_groups)

            new_rules = []
            origin_rules = subscription_config.get("rules", [])
            for rule_str in origin_rules:
                # if "中国" in rule_str:
                #     continue
                rules_res = rule_str.split(',')
                if len(rules_res) == 3:
                    domain_name = rules_res[1]
                    if domain_name in global_rules:
                        continue
                    if "全球" in rule_str:
                        continue
                    global_rules.append(domain_name)
                    new_rules.append(rule_str)
            aggregated_config["rules"].extend(new_rules)
        except Exception as e:
            logger.error(e)
    return aggregated_config


if __name__ == "__main__":
    subscription_links = ["https://nodefree.org/dy/2023/08/20230831.yaml",
"https://clashnode.com/wp-content/uploads/2023/08/20230831.yaml"]
# ]  # 替换为实际的订阅链接 "https://clashnode.com/wp-content/uploads/2023/08/20230830.yaml"
    aggregated_config = aggregate_clash_subscriptions(subscription_links)
    with open("../merged_config20230818.yaml", 'w', encoding="utf-8") as file:
        with open("../../static/proxy_head.txt", 'r') as head_file:
            lines = head_file.readlines()
            for line in lines:
                file.write(line)

        # yaml.dump(aggregated_config, file, default_flow_style=False, allow_unicode=True)
