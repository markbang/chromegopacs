import requests
import re
import json
import geoip2.database
import socket

def fetch_github_files(username, repository, file_paths):
    base_url = f"https://raw.githubusercontent.com/{username}/{repository}/master/"
    results = {}
    for file_path in file_paths:
        url = base_url + file_path
        try:
            response = requests.get(url)
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
        return None
    
    
# 示例用法
username = "Alvin9999"
repository = "pac2"
file_paths = ["hysteria2/config.json", "hysteria2/1/config.json", "hysteria2/13/config.json", "hysteria2/2/config.json"]
pac_list = []
results = fetch_github_files(username, repository, file_paths)
for file_path, content in results.items():
    if content:
        pac_list.append(convert_to_hyproxy(content))
with open('hy2pac.txt','w') as f:
    f.write('\n'.join(pac_list))


    
        

