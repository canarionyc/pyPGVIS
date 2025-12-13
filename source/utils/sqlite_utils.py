import sqlite3

def get_data_from_sqlite(db_path):
    """
    Connects to a SQLite database to extract the model name.

    Args:
        db_path (str): The full path to the SQLite database file.

    Returns:
        dict: A dictionary containing the model name, 
              or None if the data cannot be retrieved.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Initialize a dictionary to hold the extracted data
        data = {
            "model_name": None,
        }

        # Attempt to extract the model name
        try:
            cursor.execute("SELECT name FROM models")
            result = cursor.fetchone()
            if result:
                data["model_name"] = result[0]
        except sqlite3.Error as e:
            print(f"Could not retrieve model name: {e}")

        conn.close()
        return data

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

if __name__ == '__main__':
    # Example usage with the provided database path
    db_file = r"C:\ProyectosCTEyCEE\CTEHE2019\Proyectos\EjemploI_2526_Option1_Config1\ejemploI_2526_option1_config1_model_indicators.db"
    extracted_data = get_data_from_sqlite(db_file)

    if extracted_data:
        print("Successfully extracted data:")
        print(f"  Model Name: {extracted_data.get('model_name', 'Not Found')}")
