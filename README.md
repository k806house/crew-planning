# Crew planning

### Запуск всех сервисов локально
```
cd cicd && ./run_dev.sh
```

### Запуск бэка локально
```
cd cicd && ./run_dev.sh --server
```

### Запуск фронта локально
```
cd cicd && ./run_dev.sh --client
```

### Деплой на виртуалку
1. Зайти на гитхабе в Actions
2. Слева в Workflows выбрать нужный деплой (Run server deploy для деплоя бэка, Run client deploy для деплоя фронта)
3. Справа нажать Run workflow
4. Нажать на зеленую кнопку Run workflow

Бэк:
```
http://178.154.229.242:8080/
```

Фронт:
```
http://178.154.229.242:4200/
```
