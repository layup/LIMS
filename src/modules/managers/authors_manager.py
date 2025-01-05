import sqlite3

from base_logger import logger


class AuthorsItem:

    def __init__(self, author_id, first, last, department, title, active):
        self.author_id = author_id
        self.first = first
        self.last = last
        self.full_name = None
        self.department = department
        self.title = title
        self.active = active

        self.set_full_name()

    def set_full_name(self):

        if(self.first and self.last):
            self.full_name = f"{self.first[0].capitalize()}. {self.last.capitalize()}"

    def __repr__(self):
        return f"AuthorsItem(author_id={self.author_id}, first_name='{self.first}', last_name='{self.last}', department='{self.department}', title='{self.title}', active={self.active}, full_name='{self.full_name}')"

class AuthorsManager:

    def __init__(self, db):
        self.db = db;

        self.authors = {}

        self.init_setup()

    def init_setup(self):
        logger.info('Entering AuthorsManager init_setup')

        results = self.load_all_authors()

        if(results):
            for author in results:
                author_id = author[0]
                first_name = author[1]
                last_name = author[2]
                department = author[3]
                title = author[4]
                active = author[5]

                self.authors[author_id] = AuthorsItem(author_id, first_name, last_name, department, title, active)

                print(self.authors[author_id].__repr__)


    def load_all_authors(self):
        try:
            query = 'SELECT * FROM authors WHERE active = 1'
            results = self.db.query(query)
            return results

        except Exception as e:
            logger.error(f'Error loading authors: {e}')
            return None

    def get_authors(self):
        return self.authors

    def get_author_info(self, author_id):
        try:
            return self.authors.get(author_id)
        except KeyError:
            logger.warning(f"Author with ID {author_id} not found.")
            return None

    def add_author(self, first_name, last_name, department, title):
        logger.info(f"Entering add_author with first_name: {first_name}, last_name: {last_name}, department: {department}, title: {title}")

        active_status = 1;

        try:
            query = """INSERT INTO authors(first_name, last_name, department, title, active) VALUES(?,?,?,?,?)"""

            self.db.execute(query, (first_name, last_name, department, title, active_status))
            self.db.commit()

            if(self.db._cursor.rowcount > 0):
                author_id = self.db._cursor.lastrowid
                logger.info(f'Author added successfully: {author_id}')

                self.authors[author_id] = AuthorsItem(author_id, first_name, last_name, department, title, active_status)

                return author_id
            else:
                logger.warning("No author was inserted.")

                return None

        except Exception as e:
            logger.info(f"Error adding to table author: {e}")
            return  None

    def remove_author(self, author_id):
        logger.info(f'Entering remove_author with author_id: {author_id}')

        try:
            author_id = int(author_id)

            # Delete from the database
            query = 'DELETE FROM authors WHERE author_id = ?'
            self.db.execute(query, (author_id,))
            self.db.commit()

            deleted_rows = self.db._cursor.rowcount

            if deleted_rows > 0:
                logger.info(f"Successfully deleted {deleted_rows} row(s) from authors.")

                # Remove the item from the self.authors
                del self.authors[author_id]

                return deleted_rows

            else:
                logger.info("No rows were deleted (the condition may not have matched any records).")
                return None

        except KeyError:
            logger.error("Error deleting from self.authors: {e}")
            return None

        except Exception as e:
            logger.error(f'Error deleting from table author: {e}')
            return None

    def update_author(self, author_id, first_name, last_name, department, title, active):
        logger.info(f"Entering update_author with author_id: {author_id}")


        try:
            # Set the active status value (ensure it's 0 or 1)
            active = int(active) in (0, 1)  # Convert to int and check for valid values
            author_id = int(author_id)

            query = """
                UPDATE authors
                SET first_name = ?, last_name = ?, department = ?, title = ?, active = ?
                WHERE author_id = ?
            """
            self.db.execute(query, (first_name, last_name, department, title, active, author_id))
            self.db.commit()

            # Check if any rows were updated
            if self.db._cursor.rowcount > 0:
                logger.info(f"Author with ID {author_id} updated successfully.")
                self.authors[author_id] = AuthorsItem(author_id, first_name, last_name, department, title, active)
                return
            else:
                logger.warning(f"No author found with ID {author_id} for update.")
                return None

        except sqlite3.Error as e:
            logger.error(f"Error updating author: {e}")
            return None

        except Exception as e:
            logger.error(f'Error adding to self.authors: {e}')
            return None


