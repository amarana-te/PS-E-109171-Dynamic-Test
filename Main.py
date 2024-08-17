from Operations import read_files, get_info, update_tests, disable_tests
import json

OAUTH = ""

headers = {
        'Authorization' : 'Bearer ' + OAUTH,
        'Content-Type' : 'application/json'
    }

def main(directory_path):

   
    cvs_agents = read_files(directory_path)
    print(f'Data gathered from the .json file: {cvs_agents} \n ')
    print("===========================================================")

    if cvs_agents:

        #obtenemos info de TE
        print(f'The information on the JSON was updated. New config will be pushed... \n')

        cvs_agents = get_info(headers, data=cvs_agents)

        print("===========================================================")

        print(f'This is the assignment information for this agent: \n{json.dumps(cvs_agents,indent=4)} \n')

        print("===========================================================\n")

        cvs_agents = update_tests(cvs_agents, headers)

        print("\n===========================================================")
        print(f'\n Unassign agents from previous run...\n')
        disable_tests(cvs_agents, headers)

        print("\n===========================================================")


        


main(directory_path="cvs_folder/")