#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Ruslan Talipov'

import apsw
import json

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class ClusterizationTask(object):

    def __init__(self, feed_table, cluster_table, distance, start_location,
                 primitive_count):

        # self.connection = sqlite3.Connection('data.sqlite')
        self.connection = apsw.Connection('./../data.sqlite')
        self.connection.enableloadextension(True)
        self.connection.loadextension('/usr/lib/x86_64-linux-gnu/libspatialite.so.5')
        self.connection.enableloadextension(False)

        self.cur = self.connection.cursor()

        self.feed_table = feed_table
        self.cluster_table = cluster_table

        self.distance = distance
        self.start_location= 'POINT(%s %s)' % (start_location[0], start_location[1])
        self.primitive_count = primitive_count



    def __call__(self, *args, **kwargs):
        target_list = [self._get_first_primitive()]
        new_target_list = []

        while self.primitive_count > 0:
            if target_list:
                # print target_list
                print self.primitive_count
                for target in target_list:
                    has_neighbor_primitive = has_neighbor_cluster = True
                    # Выполняем запрос:
                        # Дай все кластеры на растоянии distance от target
                    primitive_list = self._get_neighbor_primitive_list(target)
                    # Выполняем запрос:
                        # Дай все примитивы на расстоянии distance от target
                    if primitive_list:
                        # Добавляем примитивы к таргету
                        # Уменьшая счётчик оставшихся примитивов
                        target = self._merge_object_list(target, primitive_list, True)
                    else:
                        has_neighbor_primitive = False

                    cluster_list = self._get_neighbor_cluster_list(target)
                    if not cluster_list:
                        # Если пуст добавляем таргет в списк готовых кластеров
                        self._create_cluster(target)
                        # Выкидываем из target_list
                        has_neighbor_cluster = False
                    else:
                        # Объединяем кластеры обновляя target,
                        # не забываем удалять необъединённых участников из базы
                        target = self._merge_object_list(target, cluster_list, False)
                        self._delete_cluster(cluster_list)
                        self._create_cluster(target)

                    if has_neighbor_primitive:
                        new_target_list.append(target)
                        self._update_cluster(target)

                else:
                    target_list = new_target_list
                    new_target_list = []

            else:
                target_list = self._get_target # ?



    def _get_first_primitive(self):
        # print self.feed_table, self.start_location
        self.cur.execute('''
        SELECT PK_UID, AsGeoJSON(Geometry) from %s
        WHERE Contains(Geometry, GeomFromGeoJSON(':location'))
        LIMIT 1;
        ''' % self.feed_table, {'location':self.start_location}
        )
        for primitive in self.cur.fetchall():
            if primitive:
                return primitive
            else:
                return None


    def _get_target(self):
        pass

    def _get_neighbor_primitive_list(self, primitive):
        '''
        Достаём всех ближайших соседей
        '''
        # print primitive
        self.cur.execute('''
            SELECT candidate.PK_UID, AsGeoJSON(candidate.Geometry)
                FROM %s AS target, %s AS candidate
                WHERE target.PK_UID = ? AND
                candidate.PK_UID <> target.PK_UID AND
                Distance(target.Geometry, candidate.Geometry) < ?;
            ''' % (self.feed_table, self.feed_table),
            (primitive[0], self.distance)
        )
        object_list = [i for i in self.cur]
        return object_list
        # for row in self.cur:
        #     print 'yield neighbor_primitive_list'
        #     yield row

    def _get_neighbor_cluster_list(self, primitive):
        '''
        Достаём все ближайшие кластера
        '''
        self.cur.execute('''
            SELECT candidate.PK_UID, AsGeoJSON(candidate.Geometry)
                FROM %s AS target, %s AS candidate
                WHERE target.PK_UID = ? AND
                candidate.PK_UID <> target.PK_UID AND
                Distance(target.Geometry, candidate.Geometry) < ?;
            ''' % (self.feed_table, self.cluster_table),
            (primitive[0], self.distance)
        )
        object_list = [i for i in self.cur]
        return object_list
        # for row in self.cur:
        #     print 'yield neighbor_cluster_list'
            # yield row

    def _merge_object_list(self, target, objects_list=[], is_primitive=True):
        '''
        Сливаем мультиполигоны
        '''
        import pprint
        target = list(target)
        target[1] = json.loads(target[1])

        logging.info(target)

        target[1]['coordinates'] = list(target[1]['coordinates'])
        for object_ in objects_list:
            object_ = list(object_)
            object_[1] = json.loads(object_[1])
            target[1]['coordinates'] += object_[1]['coordinates']
            if is_primitive:
                self.primitive_count -= 1
        target[1] = json.dumps(target[1])

        logging.info(target)

        return target

    def _create_cluster(self, target):
        '''
        Добавляем новый кластер
        '''
        # print "INSERT INTO clusters (PK_UID,Geometry) VALUES (Null, GeomFromGeoJSON('%s'))" % target[1]
        self.cur.execute('''
        INSERT INTO clusters (PK_UID,Geometry) VALUES ( Null , GeomFromGeoJSON('%s'))
        ;'''% target[1]) # % target[1]


    def _update_cluster(self, target):
        self.cur.execute('''
        UPDATE clusters SET Geometry = GeomFromGeoJSON('%s') WHERE PK_UID = %s ;
        ;'''% (target[1],target[0]))

    def _delete_cluster(self, cluster_list):

        if len(cluster_list) > 1:
            query = '''DELETE FROM clusters WHERE PK_UID IN %s;''' % str(tuple([i[0] for i in cluster_list]))
        else:
            query = '''DELETE FROM clusters WHERE PK_UID =  %s;''' % cluster_list[0][0]

        self.cur.execute(query)

if __name__ == '__main__':
    task = ClusterizationTask(
        feed_table = 'test_buildings',
        cluster_table = 'clusters',
        distance = 0.0005,
        start_location = (60.607481, 56.834037),
        primitive_count = 299
    )
    task()