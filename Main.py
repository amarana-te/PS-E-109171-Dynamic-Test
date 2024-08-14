from Operations import read_files, get_info, turn_off_tests, provision_agents

OAUTH = ""

headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }

def main(directory_path):

    #leer jsons para obtener toda la info guardada
    cvs_agents = read_files(directory_path)
    
    #obtenemos info de TE
    cvs_agents = get_info(headers, data=cvs_agents)

    cvs_agents = provision_agents(cvs_agents, headers)


    turn_off_tests(cvs_agents, headers)


main(directory_path="cvs_folder/")