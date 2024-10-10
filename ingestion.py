import os
import requests
import pandas as pd


def retrieve_lucca_data(url_suffix, params):
    """
    Retrieve data from the Lucca API.

    Sends a GET request to the Lucca API using the provided URL suffix
    and query parameters. Authentication is done using environment variables.

    Args:
        url_suffix (str): The URL suffix for the API endpoint.
        params (dict): Query parameters for the request.

    Returns:
        list: A list of items from the API response.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    url_api_lucca = os.getenv("URL_API_LUCCA")
    token_api_lucca = os.getenv("TOKEN_API_LUCCA")

    headers = {"Accept": "application/json",
                "Authorization" : f"lucca application={token_api_lucca}"}


    try:
        response = requests.get(url=url_api_lucca+url_suffix, headers=headers, params=params)
        data_json = response.json()
        data = data_json["data"]["items"]

        return data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def save_to_csv(data, name):
    """
    Save data to a CSV file.

    Converts the given data into a pandas DataFrame and writes it to a
    CSV file with the specified name.

    Args:
        data (list or dict): The data to save. Should be in a 
                             format that can be converted to a DataFrame.
        name (str): The name of the CSV file (including .csv extension) 
                    to which the data will be saved.
    """
    df = pd.DataFrame(data)
    df.to_csv(name, index=False)

def create_employees_list(fields):
    """
    Create a combined list of current and former employees.

    Retrieves employee data from the Lucca API, including current employees
    and former employees with no contract end date. Extracts department names
    for each employee and returns the combined list.

    Args:
        fields (list): The fields to retrieve for each employee.

    Returns:
        list: A list of employees, each including their name and department.
    """
    # Define the user API endpoint to retrieve.
    user_suffix = "/api/v3/users"

    # Retrieve current employees from the Lucca API.
    params = {"fields" : fields}
    current_employees_list = retrieve_lucca_data(user_suffix, params)

    # Retrieve former employees.
    params = {"dtContractEnd" : "notequal,null",
          "fields" : fields}
    former_employees_list = retrieve_lucca_data(user_suffix, params)

    # Combine current and former employees into a single list and extract department names.
    employees_list = current_employees_list + former_employees_list
    for employee in employees_list:
        employee["department"] = employee["department"]["name"]
    
    return employees_list

def create_departments_list(fields):
    """
    Retrieve a list of departments from the Lucca API.

    This function fetches department data from the Lucca API using the specified
    fields to retrieve. It returns the list of departments.

    Args:
        fields (list): The fields to retrieve for each department.

    Returns:
        list: A list of departments with the specified fields.
    """
    # Define the departments API endpoint and fields to retrieve and retrieve the departments data.
    departments_suffix = "/api/v3/departments"
    params = {"fields" : fields}
    departments_list = retrieve_lucca_data(departments_suffix, params)

    return departments_list

def main():
    # Create the employees list with the choosed fields
    employees_fields = ["firstName", "lastName", "gender", "birthDate", "jobTitle", "department", "dtContractStart", "dtContractEnd"]
    employees_list = create_employees_list(employees_fields)

    # Save the combined employee list to a CSV file.
    save_to_csv(employees_list, "employees.csv")

    # Create the departments list with the choosed fields
    departments_fields = ["name", "currentUsersCount", "hierarchy"]
    departments_list = create_departments_list(departments_fields)
    
    # Save the departments list to a CSV file.
    save_to_csv(departments_list, "departments.csv")

if __name__ == "__main__":
    main()

