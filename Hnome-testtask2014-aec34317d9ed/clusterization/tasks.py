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

        # Достаём сиротский примитив Для него ищем все сопряжённые
        target = self._get_target()

        while target:
            while True:
                # создаём кластер
                target = self._create_cluster(target)
                # Для кластера достаём сопряжённые пока это возможно
                primitive_list = self._get_neighbor_primitive_list(target)
                target = self._merge_object_list(target, primitive_list, is_primitive=True)
                # cluster_list = self._get_neighbor_cluster_list(target)
                # target = self._merge_object_list(target, cluster_list, is_primitive=False)
                if not primitive_list:# and not cluster_list:
                    break
            logging.info('New target!')
            target = self._get_target() # Достаём сиротские примитивы пока пока не кончатся

        # while self.primitive_count > 0:
        #     if target_list:
        #         # print target_list
        #         print self.primitive_count
        #         for target in target_list:
        #             has_neighbor_primitive = has_neighbor_cluster = True
        #             # Выполняем запрос:
        #                 # Дай все кластеры на растоянии distance от target
        #             primitive_list = self._get_neighbor_primitive_list(target)
        #             # Выполняем запрос:
        #                 # Дай все примитивы на расстоянии distance от target
        #             if primitive_list:
        #                 # Добавляем примитивы к таргету
        #                 # Уменьшая счётчик оставшихся примитивов
        #                 target = self._merge_object_list(target, primitive_list, True)
        #             else:
        #                 has_neighbor_primitive = False
        #
        #             cluster_list = self._get_neighbor_cluster_list(target)
        #             if not cluster_list:
        #                 # Если пуст добавляем таргет в списк готовых кластеров
        #                 self._create_cluster(target)
        #                 # Выкидываем из target_list
        #                 has_neighbor_cluster = False
        #             else:
        #                 # Объединяем кластеры обновляя target,
        #                 # не забываем удалять необъединённых участников из базы
        #                 target = self._merge_object_list(target, cluster_list, False)
        #                 self._delete_cluster(cluster_list)
        #                 self._create_cluster(target)
        #
        #             if has_neighbor_primitive:
        #                 new_target_list.append(target)
        #                 self._update_cluster(target)
        #
        #         else:
        #             target_list = new_target_list
        #             new_target_list = []
        #
        #     else:
        #         target_list = self._get_target # ?



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
        target = self.cur.execute(
            '''
            SELECT PK_UID, AsGeoJSON(Geometry) FROM %s
            WHERE PK_UID IN (
                SELECT building_id FROM clusters_to_building
                WHERE cluster_id IS NULL LIMIT 1
            );
            ''' % self.feed_table
        ).fetchall()[0]

        return target

    def _get_neighbor_primitive_list(self, primitive):
        '''
        Достаём всех ближайших соседей
        '''
        self.cur.execute('''
            SELECT candidate.PK_UID, AsGeoJSON(candidate.Geometry)
                FROM %s AS target, %s AS candidate, clusters_to_building as c2b
                WHERE target.PK_UID = ? AND
                candidate.PK_UID = c2b.building_id AND
                c2b.cluster_id IS NULL AND
                Distance(target.Geometry, candidate.Geometry) < ?;
            ''' % (self.cluster_table, self.feed_table),
            (primitive[0], self.distance)
        )
        object_list = [i for i in self.cur] # добавить курсор и возвращать генератор?
        if object_list:
            logging.info('return %s primitive' % len(object_list))
        return object_list

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
            ''' % (self.cluster_table, self.cluster_table),
            (primitive[0], self.distance)
        )
        object_list = [i for i in self.cur] # добавить курсор и возвращать генератор?
        if object_list:
            logging.info('return %s clusters' % len(object_list))
        return object_list

    def _merge_object_list(self, target, objects_list=[], is_primitive=True):
        '''
        Сливаем мультиполигоны
        '''
        # Сливаем геометрию
        target = list(target)
        target[1] = json.loads(target[1])

        # logging.info(target)

        target[1]['coordinates'] = list(target[1]['coordinates'])

        for object_ in objects_list:
            object_ = list(object_)
            object_[1] = json.loads(object_[1])
            target[1]['coordinates'] += object_[1]['coordinates']

            if is_primitive:
                self.primitive_count -= 1
                # Добавляем новым примитивам привязку к цели
                self.cur.execute(
                    '''
                    UPDATE clusters_to_building SET cluster_id = ?
                    WHERE building_id = ?
                    ''', ( target[0], object_[0])
                )
            else:
                # Перепривязываем примитивы старых кластеров к новому
                self.cur.execute(
                    '''
                    UPDATE clusters_to_building SET cluster_id = ?
                    WHERE cluster_id = ?
                    ''', ( target[0], object_[0])
                )


        # Обновляем новый кластер
        target[1] = json.dumps(target[1])
        self.cur.execute(
            '''
            UPDATE clusters SET Geometry=GeomFromGeoJSON('%s')
            WHERE PK_UID = %s
            ''' % (target[1], target[0])
        )
        target = self.cur.execute(
            'SELECT PK_UID, AsGeoJSON(Geometry) FROM clusters WHERE PK_UID = %s' % target[0]
        ).fetchall()[0]
        # logging.info(target)
        # Возвращаем новый кластер
        return target


    def _create_cluster(self, target):
        '''
        Добавляем новый кластер
        входной параметр это запись building
        '''
        # print "INSERT INTO clusters (PK_UID,Geometry) VALUES (Null, GeomFromGeoJSON('%s'))" % target[1]

        self.cur.execute('''
        INSERT INTO clusters (PK_UID,Geometry) VALUES ( Null , GeomFromGeoJSON('%s'));
        ''' % target[1])

        cluster_id = self.cur.execute('''
            SELECT PK_UID FROM clusters WHERE Geometry= GeomFromGeoJSON('%s');
        ''' % target[1]).fetchall()[0][0] # ? <- %s  TypeError: You must supply a dict or a sequence

        self.cur.execute(
        '''
        UPDATE clusters_to_building
        SET
            cluster_id = %s
        WHERE building_id = %s;
        ''' % (cluster_id, target[0])
        )

        return [cluster_id, target[1]] # вернули геометрию исходного building, но уже cluster из одного компонента

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