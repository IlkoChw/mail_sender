<h3>Запуск и настройка</h3>

Поместить файлы <b>dev.env</b> и <b>test_data.json</b> по пути <b>mail_sender/</b> и <b>mail_sender/app/main_app/fixtures/</b> соответственно

Запуск контейнеров: <b>docker-compose up</b>

Загрузка фикстур: <b>docker-compose exec app python manage.py loaddata test_data.json</b>


<h3>Панель администратора</h3>

В фикстурах находятся две учетных записи с преднастроенными параметрами для рассылки:

Логин/пароль: <b>user1@mail.com qw123</b>

Логин/пароль: <b>user2@mail.com qw123</b>


<h3>Возможности</h3>
<li>У каждого пользователя отдельные настройки почты для рассылки
<li>Группировка подписчиков
<li>Создание html-шаблона или подключение внешнего файла
<li>Отложенные рассылки по заданным группам подписчиков
<li>Метод для отслеживания открытия письма подписчиком
<li>Пользователь видит только созданные собой объекты (подписчики, группы, шаблоны, рассылки)


<h3>To do</h3>
<li>Подключить массовый импорт/экспорт подписчиков
<li>Возможность пользователю подключить несколько почт для рассылки
<li>Метод для проверки подключения к smtp-серверу почты для рассылки
<li>Шифрование паролей пользователей
<li>Доработать ограничение видимости пользователей
<li>Написать тесты
<li>Отчеты для пользователя по конкретной рассылке
<li>Кастомизация админ-панели
<li>Написать веб-интерфейс для пользователей
