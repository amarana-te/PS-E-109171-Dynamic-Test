from Operations import read_files, get_info, agents2Tests, provision_agents


def main(directory_path):

    te_agents, te_tests = get_info(OAUTH="X X X X X X")

    cvs_agents = read_files(directory_path)

    te_tests = agents2Tests(te_tests, te_agents, cvs_agents)

    provisioning = provision_agents(te_tests, OAUTH="X X X X X X")

    return provisioning


print(main(directory_path="cvs_folder/"))
