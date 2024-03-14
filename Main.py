import schedule
import time
from Operations import read_files, get_info, agents2Tests, provision_agents, json_targets_func, clear_previous


def main(directory_path, OAUTH):

    print('GETTING JSON INFO ')
    cvs_agents, json_agents ,unassign_agents = read_files(directory_path)

    print('')
    print('GETTING JSON TARGETS ')
    json_targets = json_targets_func(cvs_agents)

    print('')
    print('GETTING ACCOUNTS INFO ')
    te_agents, te_tests, remove_agents = get_info(OAUTH=OAUTH, json_targets=json_targets, unassign_agents=unassign_agents, json_agents = json_agents) ## TOKEN


    print('')
    print('GETTING AGENTS AND TESTS RELATION ')
    te_tests = agents2Tests(te_tests, te_agents, cvs_agents)
    

    print('')
    print('PROVISION AGENTS STARTING')
    remove_agents = provision_agents(te_tests, remove_agents,OAUTH=OAUTH)


    print('')
    print('UNASSIGN AGENTS FROM PREVIOS RUN')
    remove_agents = clear_previous(remove_agents,OAUTH=OAUTH)




def job():
    print("Executing the scheduled task...")

    main(directory_path="cvs_folder/", OAUTH="") # ----> Variables that can be changed

    print("Execution finished, waiting for next round")
    print(" ")

# Schedule the job every day at the desired time
schedule.every().day.at("06:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
 