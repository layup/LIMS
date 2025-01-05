import sqlite3

class UnitItem:
    def __init__(self, unit_id, unit_name):
        self.unit_id = unit_id
        self.unit_name = unit_name

    def get_id(self):
        return self.unit_id

    def get_name(self):
        return self.unit_name


class UnitManager:

    def __init__(self, db):
        self.db = db;
        self.units = []

        self.init_setup()

    def init_setup(self):

        self.units = self.load_units()

    def load_units(self):
        query = 'SELECT unit_id, unit_name FROM units'

        results = self.db.query(query)

        unit_list = []

        for item in results:
            unit_id = item[0]
            unit_name = item[1]

            unit_list.append(UnitItem(unit_id, unit_name))

        return unit_list

    def get_units(self):
        return self.units

    def get_unit_names(self):

        name_list = []

        for current_unit in self.get_units():
            name_list.append(current_unit.get_name())

        return name_list

    def add_unit(self, new_unit_name):

        try:
            query = 'INSERT INTO units (unit_name) values (?)'
            self.db.execute(query, (new_unit_name, ))
            self.db.commit()

        except sqlite3.IntegrityError as e:
            print(e)
        except Exception as e:
            print(e)


    def remove_unit(self, unit_id):
        try:
            query = 'DELETE FROM units WHERE unit_id = ?'
            self.db.execute(query, (unit_id))
            self.db.commit()

            # Check how many rows were deleted
            deleted_rows = self.db.cursor.rowcount  # Get the number of deleted rows
            if deleted_rows > 0:
                print(f"Successfully deleted {deleted_rows} row(s) from chemTestsData.")
            else:
                print("No rows were deleted (the condition may not have matched any records).")

            return deleted_rows

        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")

            return None



