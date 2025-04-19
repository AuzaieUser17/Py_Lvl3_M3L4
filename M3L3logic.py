import sqlite3
from config import DATABASE

skills = [(_,) for _ in ['Python', 'SQL', 'API', 'Discord']]
statuses = [(_,) for _ in ['Prototyping', 'In Development', 'Completed', 'Updated', 'Abandoned/Not supported']]

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                                project_id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                project_name TEXT NOT NULL,
                                description TEXT,
                                url TEXT,
                                status_id INTEGER,
                                FOREIGN KEY(status_id) REFERENCES status(status_id)
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                                skill_id INTEGER PRIMARY KEY,
                                skill_name TEXT UNIQUE
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                                project_id INTEGER,
                                skill_id INTEGER,
                                FOREIGN KEY(project_id) REFERENCES projects(project_id),
                                FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                                status_id INTEGER PRIMARY KEY,
                                status_name TEXT UNIQUE
                            )''')
            conn.commit()
        print("Database created successfully")

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
    
    # Public accessor for __select_data
    def select_data(self, sql, data=tuple()):
        return self.__select_data(sql, data)

    def default_insert(self):
        self.__executemany('INSERT OR IGNORE INTO skills (skill_name) VALUES (?)', skills)
        self.__executemany('INSERT OR IGNORE INTO status (status_name) VALUES (?)', statuses)

    def insert_project(self, data):
        sql = 'INSERT OR IGNORE INTO projects (user_id, project_name, url, status_id) VALUES (?, ?, ?, ?)'
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES (?, ?)'
        self.__executemany(sql, data)

    def get_statuses(self):
        return self.__select_data('SELECT status_name FROM status')

    def get_status_id(self, status_name):
        res = self.__select_data('SELECT status_id FROM status WHERE status_name = ?', (status_name,))
        return res[0][0] if res else None

    def get_projects(self, user_id):
        return self.__select_data('SELECT * FROM projects WHERE user_id = ?', (user_id,))

    def get_project_id(self, project_name, user_id):
        return self.__select_data(
            'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', (project_name, user_id))[0][0]

    def get_skills(self):
        return self.__select_data('SELECT * FROM skills')

    def get_project_skills(self, project_name):
        res = self.__select_data('''SELECT skill_name FROM projects 
                                    JOIN project_skills ON projects.project_id = project_skills.project_id 
                                    JOIN skills ON skills.skill_id = project_skills.skill_id 
                                    WHERE project_name = ?''', (project_name,))
        return ', '.join([x[0] for x in res])

    def get_project_info(self, user_id, project_name):
        sql = '''SELECT project_name, description, url, status_name FROM projects 
                 JOIN status ON status.status_id = projects.status_id 
                 WHERE project_name = ? AND user_id = ?'''
        return self.__select_data(sql, (project_name, user_id))

    def update_projects(self, param, data):
        self.__executemany(
            f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?", [data])

    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?"
        self.__executemany(sql, [(skill_id, project_id)])


# === TESTING SECTION ===
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)

    # Step 1: Setup
    manager.create_tables()
    manager.default_insert()

    # Step 2: Insert project
    user_id = 1
    project_name = "Aplikasi Discord Bot"
    project_url = "https://github.com/user/discord-bot"
    status_id = manager.get_status_id("In Development")
    manager.insert_project([(user_id, project_name, project_url, status_id)])

    # Step 3: Insert skills
    manager.insert_skill(user_id, project_name, "Python")
    manager.insert_skill(user_id, project_name, "Discord")

    # Step 4: Display all statuses
    print("\nStatus List:")
    for status in manager.get_statuses():
        print("-", status[0])

    # Step 5: Display all skills
    print("\nSkill List:")
    for skill in manager.get_skills():
        print("-", skill[1])

    # Step 6: Display all projects for user_id
    print("\nProjects for user 1:")
    for project in manager.get_projects(user_id):
        print(project)

    # Step 7: Get project info
    print("\nProject Info:")
    print(manager.get_project_info(user_id, project_name))

    # Step 8: Show project skills
    print("\nProject Skills:")
    print(manager.get_project_skills(project_name))

    # # FOR TESTING M3L3 USE THIS CODE UP TO STEP 11
    # # Step 9: Update project name
    # new_project_name = "Discord Automation Bot"
    # manager.update_projects("project_name", (new_project_name, project_name, user_id))

    # print("\nAfter Project Name Update:")
    # print(manager.get_project_info(user_id, new_project_name))

    # # Step 10: Delete a skill from project
    # project_id = manager.get_project_id(new_project_name, user_id)
    # skill_id = manager.select_data("SELECT skill_id FROM skills WHERE skill_name = 'Discord'")[0][0]
    # manager.delete_skill(project_id, skill_id)

    # print("\nAfter Deleting 'Discord' Skill:")
    # print(manager.get_project_skills(new_project_name))

    # # Step 11: Delete the project
    # manager.delete_project(user_id, project_id)

    # print("\nAfter Deleting Project:")
    # print(manager.get_projects(user_id))