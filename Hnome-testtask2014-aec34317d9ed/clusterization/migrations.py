#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'
import apsw
import sys
import sqlite3

def init_clusterization():
    '''
    CREATE TABLE building (
    PK_UID INTEGER PRIMARY KEY AUTOINCREMENT,
    "BUILDING" TEXT,
    "A_STRT" TEXT,
    "A_SBRB" TEXT,
    "A_HSNMBR" TEXT,
    "B_LEVELS" TEXT,
    "NAME" TEXT,
    "Geometry" MULTIPOLYGON);

    CREATE TABLE clusters (
    PK_UID INTEGER PRIMARY KEY AUTOINCREMENT,
    "Geometry" MULTIPOLYGON);

    CREATE TRIGGER "ggi_building_Geometry" BEFORE INSERT ON "building"
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, 'building.Geometry violates Geometry constraint [geom-type or SRID not allowed]')
        WHERE (SELECT type FROM geometry_columns
        WHERE f_table_name = 'building' AND f_geometry_column = 'Geometry'
        AND GeometryConstraints(NEW."Geometry", type, srid, 'XY') = 1) IS NULL;
    END;

    CREATE TRIGGER "ggu_building_Geometry" BEFORE UPDATE ON "building"
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, 'building.Geometry violates Geometry constraint [geom-type or SRID not allowed]')
        WHERE (SELECT type FROM geometry_columns
        WHERE f_table_name = 'building' AND f_geometry_column = 'Geometry'
        AND GeometryConstraints(NEW."Geometry", type, srid, 'XY') = 1) IS NULL;
    END;

    CREATE TRIGGER "gid_building_Geometry" AFTER DELETE ON "building"
    FOR EACH ROW BEGIN
        DELETE FROM "idx_building_Geometry" WHERE pkid=OLD.ROWID;
    END;

    CREATE TRIGGER "gii_building_Geometry" AFTER INSERT ON "building"
    FOR EACH ROW BEGIN
        DELETE FROM "idx_building_Geometry" WHERE pkid=NEW.ROWID;
        SELECT RTreeAlign('idx_building_Geometry', NEW.ROWID, NEW."Geometry");
    END;

    CREATE TRIGGER "giu_building_Geometry" AFTER UPDATE ON "building"
    FOR EACH ROW BEGIN
        DELETE FROM "idx_building_Geometry" WHERE pkid=NEW.ROWID;
        SELECT RTreeAlign('idx_building_Geometry', NEW.ROWID, NEW."Geometry");
    END;
    '''
    pass

def create_clusters():
    connection = apsw.Connection('./../data.sqlite')
    # connection = sqlite3.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    cursor.execute(
        '''
        CREATE TABLE clusters (
        PK_UID INTEGER PRIMARY KEY AUTOINCREMENT,
        "Geometry" MULTIPOLYGON);
        '''
    )
    cursor.close()
    connection.close()


def create_test_buildings():
    connection = apsw.Connection('./../data.sqlite')
    # connection = sqlite3.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    cursor.execute(
        '''
        CREATE TABLE test_buildings (
        PK_UID INTEGER PRIMARY KEY AUTOINCREMENT,
        "Geometry" MULTIPOLYGON);
        '''
    )
    cursor.execute(
        '''
        SELECT AsText(Geometry) from building
        WHERE
         MBRContains(BuildMBR(60.58859660568276, 56.83316153126612, 60.615719103240956, 56.837962490083946), Geometry)
        LIMIT 500;
        '''
    )

    for item in cursor.fetchall():
        cursor.execute(
            '''
            INSERT INTO test_buildings (PK_UID,Geometry)
            VALUES (Null, GeomFromText('%s'));
            ''' % item[0]
        )

def create_clusters_to_building(test=True):
    connection = apsw.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    if test:
        building = 'test_buildings'
    else:
        building = 'building'
    cursor.execute(
        '''
        CREATE TABLE clusters_to_building (
            PK_UID INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_id INTEGER DEFAULT Null,
            building_id INTEGER,
            FOREIGN KEY (cluster_id)  REFERENCES clusters(PK_UID),
            FOREIGN KEY (building_id) REFERENCES %s(PK_UID)
        );
        ''' % building
    )
    cursor.close()
    connection.close()

def destroy_test_buildings():
    connection = apsw.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    cursor.execute(
        '''
        DROP TABLE test_buildings;
        '''
    )
    cursor.close()
    connection.close()

def destroy_clusters_to_building():
    connection = apsw.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    cursor.execute(
        '''
        DROP TABLE clusters_to_building;
        '''
    )
    cursor.close()
    connection.close()

def destroy_clusters():
    connection = apsw.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    cursor.execute(
        '''
        DROP TABLE clusters;
        '''
    )
    cursor.close()
    connection.close()

def prepare_clusters_to_building():
    connection = apsw.Connection('./../data.sqlite')
    connection.enableloadextension(True)
    connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
    connection.enableloadextension(False)
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    for item in cursor.execute(
        '''
        SELECT PK_UID FROM test_buildings
        '''
    ):
        cursor2.execute(
            '''
            INSERT INTO clusters_to_building
            VALUES (Null, Null, %s)
            ''' % item[0]
        )

    cursor.close()
    connection.close()

def setup():
    func_list = globals()
    for f in [
        'destroy_clusters_to_building',
        'destroy_clusters',
        'create_clusters',
        'create_clusters_to_building',
        'prepare_clusters_to_building'
    ]:
        try:
            func_list[f]()
        except Exception, q:
            print Exception, q



if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        globals()[args[1]]()
    else:
        print 'Fail %s' % args