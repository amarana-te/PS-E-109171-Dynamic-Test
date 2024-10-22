from Connector import get_data


url = "https://api.thousandeyes.com/v7/agents"

payload = {"aid": 2087777, "agentTypes": "enterprise"}
headers = {
  'Accept': 'application/hal+json',
  'Authorization': 'Bearer f7aa3b68-caa0-4a92-9215-432786e32052'
}

status, response = get_data(headers=headers, endp_url=url, params=payload)

print(response)