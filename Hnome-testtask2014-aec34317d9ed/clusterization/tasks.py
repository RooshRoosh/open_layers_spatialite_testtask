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
        target = self._create_cluster(target)
        target_count = 1
        while target:
            while True:
                # создаём кластер
                # Для кластера достаём сопряжённые пока это возможно
                primitive_list = self._get_neighbor_primitive_list(target)
                target = self._merge_object_list(target, primitive_list, is_primitive=True)
                logging.info('Осталось %s примитивов' %self.primitive_count)
                if not primitive_list:
                    break
            target = self._get_target() # Достаём сиротские примитивы пока пока не кончатся
            target = self._create_cluster(target)
            target_count+=1
            logging.info('Новая цель #%s' % target_count)
        logging.warning('Расчёт завершён')


    def _get_target(self):
        result = self.cur.execute(
            '''
            SELECT PK_UID, AsGeoJSON(Geometry) FROM %s
            WHERE PK_UID IN (
                SELECT building_id FROM clusters_to_building
                WHERE cluster_id IS NULL LIMIT 1
            );
            ''' % self.feed_table
        ).fetchall()
        if result:
            target = result[0]
        else:
            target = None
        return target

    def _get_neighbor_primitive_list(self, primitive):
        '''
        Достаём всех ближайших соседей
        '''
        self.cur.execute('''
            SELECT candidate.PK_UID, AsGeoJSON(candidate.Geometry)
                FROM %s AS target, %s AS candidate
                WHERE target.PK_UID = ? AND
                candidate.PK_UID IN (SELECT building_id FROM clusters_to_building c2b WHERE c2b.cluster_id IS NULL)
                AND Distance(target.Geometry, candidate.Geometry) < ?;
            ''' % (self.cluster_table, self.feed_table),
            (primitive[0], self.distance)
        )
        object_list = [i for i in self.cur] # добавить курсор и возвращать генератор?
        if object_list:
            logging.info('Для текущей цели найдено %s сопряжённых примитивов' % len(object_list))
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
        self.primitive_count-=1
        return [cluster_id, target[1]] # вернули геометрию исходного building, но уже cluster из одного компонента

if __name__ == '__main__':
    task = ClusterizationTask(
        feed_table = 'buildings',#'test_buildings',
        cluster_table = 'clusters',
        distance = 0.0005,
        start_location = (60.607481, 56.834037),
        primitive_count = 299
    )
    task()