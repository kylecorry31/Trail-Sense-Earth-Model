from scripts import opencellid, progress
import sqlite3
import os

db_path = 'output/cell_towers.db'

if not os.path.exists('output'):
    os.makedirs('output')

opencellid.download()
towers = opencellid.process()

if os.path.exists(db_path):
    os.remove(db_path)

db = sqlite3.connect(db_path)
cursor = db.cursor()

# Create a new table to store the cell towers.
cursor.execute('''
    CREATE TABLE cell_towers(
        radios INTEGER,
        latitude INTEGER,
        longitude INTEGER
    )
''')

with progress.progress("Creating cell tower database", len(towers)) as pbar:
    for tower in towers.keys():
        tower = {
            'radios': towers[tower],
            'latitude': int(tower[0] * 10),
            'longitude': int(tower[1] * 10),
        }
        cursor.execute('''
            INSERT INTO cell_towers(radios, latitude, longitude)
            VALUES(:radios, :latitude, :longitude)
        ''', tower)
        pbar.update(1)

db.commit()
db.close()