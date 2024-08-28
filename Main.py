from Operations import read_files, get_info, update_tests, disable_tests
import json

OAUTH = ""

headers = {
    'Authorization': 'Bearer ' + OAUTH,
    'Content-Type': 'application/json'
}

def main(directory_path):
    
    try:
        
        cvs_agents = read_files(directory_path)
        if not cvs_agents:
        
            print(f"No data found in the provided directory: {directory_path}. Please check if the directory contains valid JSON files.")
            return


        print(f'Data gathered from the .json file: {cvs_agents} \n ')
        print("===========================================================")

        print('The information on the JSON was updated. New config will be pushed... \n')

        cvs_agents = get_info(headers, data=cvs_agents)
        
        if cvs_agents is None:
        
            print("Failed to retrieve information from the ThousandEyes API. Please check your connection and API credentials.")
            return

        print("===========================================================")
        print(f'This is the assignment information for this agent: \n{json.dumps(cvs_agents, indent=4)} \n')
        print("===========================================================\n")

        cvs_agents = update_tests(cvs_agents, headers)
        
        if cvs_agents is None:
        
            print("Failed to update tests. Please ensure the data is correctly formatted and the API is accessible.")
            return

        print("\n===========================================================")
        print('\n Unassign agents from previous run...\n')
        
        disable_tests(cvs_agents, headers)

        print("\n===========================================================")

    except FileNotFoundError as e:
        
        print(f"Error: The directory or file was not found: {e}. Please provide a valid directory path.")
    
    except json.JSONDecodeError as e:
    
        print(f"Error: Failed to decode JSON data. Please check the input files for valid JSON format. Details: {e}")
    
    except TypeError as e:
    
        print(f"Error: An unexpected data type was encountered: {e}. Please check the data returned from the API and ensure it's in the expected format.")
    
    except Exception as e:
    
        print(f"An unexpected error occurred: {e}. Please check the logs for more details.")

if __name__ == "__main__":

    main(directory_path="cvs_folder/")
