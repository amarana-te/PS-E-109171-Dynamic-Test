data = [
    {
        "name": "thousandeyes_68500.localdomain",
        "urls": ["https://10.6.65.122:7191/RxConnectRxP/"]
    },
    {
        "name": "thousandeyes_12345.localdomain",
        "urls": ["https://10.6.65.123:7191/RxConnectRxP/", "https://10.6.65.122:7191/RxConnectRxP/"]
    }
]



def get_targets_list(data:list):

    target_list = []
    for target in data:

        urls = target.get("urls", [])

        for url in urls:
        
            if url not in target_list:
        
                target_list.append(url)

    return target_list


print(get_targets_list(data))