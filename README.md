Добрый день, данный github репозиторий служит примером того что все описанные навыки в резюме/сопроводительном письме имеют под собой какое то основание. Тут описано то как я выстраивал экосистему сервера.

# Начнём с железа. 
* МатПлата: Нuаnаn Х79G v1.51
* Процессор: Intеl Хеоn 2650v2
* ОЗУ: 64gb ddr3
* Накопитель: Полужевой hdd

Да китайское железо с ali, да диск скоро сдохнет, да я скоро упрусь в производительность(уже упёрся), но это единственный более мене нормальный вариант за цена\качество.

# Программное обеспечение

Задумка заключается в том что на один мощный вычислительный узел поставить OS для виртуализации, а после создавать отдельные виртуальные машины под определённые задачи, да так теряется часть производительности, но зато всё лежит на своих места и никто никому не мешает. На самом сервере стоит ProxMox, почему именно ProxMox а не VMware и прочие аналоги? Во первых ProxMox использовали на моём прошлом месте работы, из за чего я к нему более менее привык, во вторых на ProxMox много гайдов, в третьих ProxMox не говорит что я русня которую надо везде забанить. 

# Структура сервера
 
![text](http://37.194.133.101:5454/media/posts/1.png)

Основной узел самого ProxMox называется samovar, подразумевалось что получится всё автоматизировать, и ручками нечего не придется делать(а ещё мне показалось это забавным). На основном узле настроены шаблоны для более быстрого развертывания, если что то простое и не требовательное используется шаблон контейнера ProxMox, если что то более серьёзное то шаблон с облачным образом ubuntu, в данным момент основным шаблоном является ubuntu редакции noble. 

# Контейнеры

![text](http://37.194.133.101:5454/media/posts/docker.jpg)

Начнём по порядку, сначала у нас идут контейнеры созданные с помощью самого ProxMox. Один из контейнеров это виртуалка выделенная отдельно под контейнеры docker. На данный момент там поднять мой проект, БД MySQL и NextCloud, filebrowser,также от друзей поступила просьба поднять minecraft сервер, но так как дефолтный контейнер предполагает наличие лицензии, нечего не вышло. 
Второй контейнер выделен исключительно под тесты, запуск только что написанных скриптов, триллион образов не рабочих контейнеров docker, ну и в принципе виртуалка которую не жалко.

# Main-server

После контейнеров ProxMox у нас идёт основной узел всей эко системы, main-server, на нём установлен ansible, для управления другими узлами, в основном playbook для управления узлами кластера kuber или перенос docker контейнеров на определённую виртуалку и запуск оных, также на нём установлен kubectl и helm, для более удобного управления кластером kubernetes, с него запускаются все deploy и helm chart, до этого я хранил всё это на главной мастер ноде, но после того как пришлось пересобирать весь кластер я об этом пожалел, так что теперь всё храню в едином месте. По сути это узел предназначенный для управления другими, является так скажем точкой входа для управления, да по идеи его можно было не создавать а подключаться к самому ProxMox, но учитывая факт того что ProxMox это надстройка на Debian, и из за этого некоторые элементы могли отсутствовать, я предпочёл создать main узел на ubuntu и не парить себе мозг. 

# Jenkins

![text](http://37.194.133.101:5454/media/posts/jenkins.png)

В Jenkins я по большей части использую  Pipeline, задачи с свободной конфигурацией я тоже использовал, но по большей части только в начали, ибо Pipeline в более понятной форме показывает где ты ошибся.  
По большей части всё строиться по одной схеме.  
![text](http://37.194.133.101:5454/media/posts/2.png)  
Разработчик делает коммит на github, с github прилетает webhuk на jenkins, jenkins делает клон github на тестовый узел (не хочу мусорить на jenkins узле), после чего на тестовом узле собирается образ docker контейнера и отправляется на dockerhub, как образ будет готов jenkins через main-server запускает helm для обновления deploy. Таким образом работает проект написаны мной, тестовый проект который был создан чтобы протестировать данный алгоритм.
Есть ещё одна версия, но она более упрощённая.  
![text](http://37.194.133.101:5454/media/posts/3.png)  
Разработчик делает коммит на github, с github прилетает webhuk на jenkins, jenkins в свою очередь копирует необходимые данные с github в определённый репозиторий в jenkins-test(там запущен nginx) через Publish Over SSH. 
# kubernetes
То на что я убил максимальное количество времени и усилий, сам кластер базируется на k3s, k3s я выбрал потому что он свободно распространяется, на нём строят высоко нагруженные кластера, на него есть документация и большая поддержка от комьюнити. Да minikube тоже поставляется свободно, но на мой взгляд это по большей части плацдарм для обучения, несколько узлов в нём не поднять, Load Balancer там не поднять, в глобальную сеть его можно вывести через тюнель, так что minikube отвалился довольно быстро. k8s тоже не подошёл, ибо чтобы его нормально запустить потребовалось бы заплатить не плохие день Yandex или Vk, чтобы получить доступ к Cloud инструментам, а про Google и Amazon я вообще молчу.  
Структура кластера строиться следующим образом. 

![text](http://37.194.133.101:5454/media/posts/4.png)  

Есть 3 master, если один из мастеров по какой то причине выходит из строя  на его место встают 2 оставшихся, тоже самое с рабочими, в планах было поднять ещё отдельный узел под хранилище с помощью longhorn, но пока что не получилось. В кластере установлен KubeVIP для возможности подключения всех узлов, в роле Load Balancer выступает metalLB, для возможности управлять кластером через UI был установлен Rancher, хотя по итогу я им не особо пользовался, ведь для автоматизации процесса проще использовать Helm. На данный момент в кластере поднят мой проект, тестовый проект связанный с jenkins, mysql, phpmyadmin, postgresql, pgadmin, в планах было поднять ещё Prometheus и Grafana, но учитывая факт того что ProxMox и Rancher предоставляют актуальное состояние узлов с графиками, и я решил лишний раз не нагружать узлы.
# Доступ

Сервер находиться у меня дома, так что доступ из вне обеспечивается пробросом портов через мой роутер. Изначально была идея установить MikrotikOS на VPS сервер, поднять там VPN и прокинуть туннель до сервера, но там были проблемы и с сомой MikrotikOS, без лицензии всё работает крайне туго, да и по цене это выходило уж как то круто. В данный момент из вне доступен только NextCloud (http://my-samovar.duckdns.org:5682/login), Jenkins(его в целях безопасности скидывать не буду), filebrowser (http://my-samovar.duckdns.org:9090), и docker контейнер с моим приложением (http://my-samovar.duckdns.org:5454/). 

# Планы 

* Купить более мощное сетевое оборудование, ибо иногда чувствуется что скорость так себе.
* Заменить полуживые hdd на ssd. 
* Купить более мощное сетевое оборудование, ибо иногда чувствуется что скорость так себе.
* Поднять ещё один узел ProxMox но уже с Windows Server, чтобы настроить там систему удалённых рабочих столов, и имень доступ к мощному железу откуда угодно.
* Освоить инструмент "Kafka"



