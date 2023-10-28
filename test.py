import yaml
import requests
# 读取 .yaml 文件
response = requests.get("https://raw.githubusercontent.com/Alvin9999/pac2/master/clash.meta2/2/config.yaml")
response.encoding = 'utf-8'
data = yaml.safe_load(response.text)
print(data)
# 构建 `hysteria` URL
server_info = data['proxies'][0]
if server_info['type'].startswith("hysteria"):
            
    url = f"hysteria://{server_info['server']}:{server_info['port']}/?auth={server_info['auth-str']}&upmbps={server_info['up'].split(' ')[0]}&downmbps={server_info['down'].split(' ')[0]}&alpn={server_info['alpn'][0]}"
        
# 打印构建的 `hysteria` URL
print(url)
