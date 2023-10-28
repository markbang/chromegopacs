import requests
import re
import json
import geoip2.database
import socket
from datetime import datetime
import yaml

protocol = {"hysteria2": "hy2", "hysteria": "hysteria","tuic": "tuic"}
def fetch_github_files(username, repository, file_paths):
    base_url = f"https://raw.githubusercontent.com/{username}/{repository}/master/"
    results = {}
    for file_path in file_paths:
        url = base_url + file_path
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                results[file_path] = response.text
            else:
                print(f"Request for {file_path} failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request for {file_path} failed with error {e}")
            results[file_path] = None
    return results

def convert_to_hyproxy(json_string):
    try:
        data = json.loads(json_string)
        server = data.get('server')
        auth = data.get('auth')
        tls = data.get('tls')
        insecure = tls.get('insecure') if tls else False
        sni = tls.get('sni') if tls else None
        location = get_physical_location(server)

        hyproxy_string = f"hy2://{auth}@{server}/?insecure={int(insecure)}"
        if sni:
            hyproxy_string += f"&sni={sni}"
        if location:
            hyproxy_string += f"#{location}"

        return hyproxy_string

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def convert_to_hysteria(json_string):
    try:
        json_data = json.loads(json_string)
        location = get_physical_location(json_data['server'])
        hysteria_string = f"hysteria://{json_data['server']}/?insecure=1&peer={json_data['server_name']}&auth={json_data['auth_str']}&upmbps={json_data['up_mbps'] * 5}&downmbps={json_data['down_mbps'] * 2}&alpn={json_data['alpn']}#{location}"
        return hysteria_string
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
def convert_to_all(content):
    try:
        data = yaml.safe_load(content)
        server_info = data['proxies'][0]
#        if server_info['type'].startswith("hysteria"): 
#             return None        
#            all_string = f"hysteria://{server_info['server']}:{server_info['port']}/?auth={server_info['auth-str']}&upmbps={server_info['up'].split(' ')[0]}&downmbps={server_info['down'].split(' ')[0]}&alpn={server_info['alpn'][0]}#{get_physical_location(server_info['server'])}"
        if server_info['type'].startswith("hysteria2"):
            all_string = f"hy2://{server_info['password']}@{server_info['server']}:{server_info['port']}/?insecure=1&sni={server_info['sni']}#{get_physical_location(server_info['server'])}"
        elif server_info['type'].startswith("tuic"):
            all_string = f"tuic://{server_info['uuid']}:{server_info['password']}@{server_info['server']}:{server_info['port']}/?congestion_control={server_info['congestion-controller']}&udp_relay_mode={server_info['udp-relay-mode']}&alpn={server_info['alpn'][0]}&allow_insecure=1#{get_physical_location(server_info['server'])}"
        else:
            return None
        return all_string

    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        return None

def get_physical_location(address):
    address = re.sub(':.*', '', address)  # 用正则表达式去除端口部分
    try:
        ip_address = socket.gethostbyname(address)
    except socket.gaierror:
        ip_address = address

    try:
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')  # 这里的路径需要指向你自己的数据库文件
        response = reader.city(ip_address)
        country = response.country.name
        city = response.city.name
        return f"{country}, {city}"
    except geoip2.errors.AddressNotFoundError as e:
        print(f"Error: {e}")
        return "Unknown"
    
    
# 示例用法
username = "Alvin9999"
repository = "pac2"
file_paths = ["hysteria2/config.json", "hysteria2/1/config.json", "hysteria2/13/config.json", "hysteria2/2/config.json", "hysteria/config.json", "hysteria/1/config.json", "hysteria/13/config.json", "hysteria/2/config.json","clash.meta2/config.yaml","clash.meta2/1/config.yaml","clash.meta2/13/config.yaml","clash.meta2/2/config.yaml","clash.meta2/15/config.yaml","clash.meta2/3/config.yaml",]
pac_list = []
results = fetch_github_files(username, repository, file_paths)
for file_path, content in results.items():
    if file_path.startswith("hysteria2"):
        pac_list.append(convert_to_hyproxy(content))
    elif file_path.startswith("hysteria"):
        pac_list.append(convert_to_hysteria(content))
    else:
        pac_list.append(convert_to_all(content))
filtered_pac_list = [item for item in pac_list if item is not None]
with open('hy2pac.txt','w') as f:
    f.write('\n'.join(filtered_pac_list))
current_time = datetime.now()
with open(f"update_time.txt", 'w') as a:
    a.write(current_time.strftime("%Y-%m-%d %H:%M:%S"))
