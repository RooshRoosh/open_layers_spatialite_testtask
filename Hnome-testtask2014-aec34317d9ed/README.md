#Сначала
Форкните репозитарий

#Потом
Установите:

* [bottle.py](http://bottlepy.org/docs/dev/tutorial.html#installation)

        $ sudo apt-get install python-bottle
    
* [apsw](http://rogerbinns.github.io/apsw/download.html)
    
        $ sudo apt-get install python-apsw
    
* [spatialite](https://www.gaia-gis.it/fossil/libspatialite/index)
    
        $ sudo apt-get install libspatialite3
  
    Для Windows используйте архив по [ссылке](https://bitbucket.org/Hnome/testtask2014/downloads/spatialite-4.0.0-DLL-win-x86.zip)

Примеры установочных команд даны для Ubuntu, установка для других ОС описана по ссылкам, приведенным выше.

#Еще чуть позже
Запустите:

    $ python server.py
    
И откройте index.html

#И вот теперь
У вас есть карта на OpenLayers и сервер, который отдает ей данные из базы данных sqlite.

Выполните задачи из следующего списка:

* Добавьте поддержку OpenLayers.Strategy.BBOX (используя индексы на серверной стороне).
* Поймите, почему если отдалить карту на несколько масштабов, а потом вернуть на исходный, все работает медленнее, чем если бы вы не делали этого.
* Исправьте это.

Bonus level (желательно выполнить или хотя бы сформулировать идеи, но не обязательно):

* Оптимизируйте код в местах, где, на ваш взгляд, он работает неоптимально
* Подумайте над способами увеличения производительности на отдаленных масштабах. Если успеете - реализуйте какой-нибудь из них.

#P.S.
Если ход решения будет отражен в истории коммитов - это будет просто прекрасно.