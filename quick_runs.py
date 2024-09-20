import os
import json, time
from datetime import datetime
from Connector import get_data, put_data

BASE_URL = "https://api.thousandeyes.com/v7/"
endp_url1 = f"{BASE_URL}account-groups"
endp_url2 = f"{BASE_URL}agents"
endp_url3 = f"{BASE_URL}tests/http-server"


data = [{'name': 'thousandeyes_68500.localdomain', 'agentId': '1325775', 'aid': '1805161', 'tests': [{'testId': '4817141', 'testDescription': '2024-09-19', 'enabled': False}], 'toRemove': [{'testId': '4161287', 'testDescription': '2024-09-19', 'agents': [{'agentId': '1325768'}]}]}, {'name': 'thousandeyes_68512.localdomain', 'agentId': '1325792', 'aid': '1805161', 'tests': [{'testId': '5797202', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '4817136', 'testDescription': '2024-09-19', 'enabled': True}], 'toRemove': [{'testId': '4161282', 'testDescription': '2024-09-19', 'agents': []}, {'testId': '4161283', 'testDescription': '2024-09-19', 'agents': []}]}, {'name': 'thousandeyes_68634.localdomain', 'agentId': '1364315', 'aid': '1805161', 'tests': [{'testId': '5797202', 'testDescription': '2024-09-19', 'enabled': True}, {'testId': '5797205', 'testDescription': '2024-09-19', 'enabled': True}], 'toRemove': [{'testId': '4817141', 'testDescription': '2024-09-19', 'agents': []}, {'testId': '4817136', 'testDescription': '2024-09-19', 'agents': []}]}]



def group_agents_by_test(data):
    target_urls = {}

    for agent in data:

        agent_id = agent['agentId']
        aid = agent['aid']
        
        # Proceso de pruebas habilitadas o deshabilitadas, omitiendo 'toRemove'
        for test in agent['tests']:
            
            test_id = test['testId']
            enabled = test['enabled']

            # Si el testId no existe, inicializamos
            if test_id not in target_urls:
                
                target_urls[test_id] = {"enabled": enabled, "agents": []}


            eas = {"agentId": agent_id}

            if eas not in target_urls[test_id]['agents']:
                
                
                target_urls[test_id]['agents'].append(eas)

    # Convertimos a la estructura requerida
    result = {
        "targetUrls": [
            {
                "testId": test_id,
                "aid": aid,
                "enabled": test_data['enabled'],
                "agents": test_data['agents']
            }
            for test_id, test_data in target_urls.items()
        ]
    }

    return result



result = group_agents_by_test(data)
print(result)

