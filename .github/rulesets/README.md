# Настройка форка: работа только через pull request

Настройки защиты веток **не копируются** при создании форка, поэтому их нужно включить
в своём форке один раз вручную. После настройки:

- в `master` нельзя пушить напрямую (и нельзя делать force-push или удалять ветку);
- изменения попадают в `master` только через pull request;
- PR можно смержить, только если прошли проверки **Tests** (тесты затронутых библиотек)
  и **Lint** (clang-tidy).

## 1. Включите GitHub Actions в форке

В форке откройте вкладку **Actions** и нажмите
*I understand my workflows, go ahead and enable them*. Без этого проверки не запускаются,
и PR смержить не получится.

## 2. Импортируйте ruleset

1. **Settings → Rules → Rulesets → New ruleset → Import a ruleset**.
2. Выберите файл [`protect-master.json`](protect-master.json) из этого каталога
   (скачайте его или возьмите из локального клона).
3. Проверьте, что *Enforcement status* — **Active**, и нажмите **Create**.

Правило применяется к ветке по умолчанию (`master`) и не имеет исключений (bypass list пуст),
поэтому действует и на владельца репозитория.

Если хочется настроить руками: *New branch ruleset*, target — *Default branch*, включить
*Restrict deletions*, *Block force pushes*, *Require a pull request before merging*
(0 approvals), *Require status checks to pass* с проверками `Tests` и `Lint`.

## Как работают проверки

Workflow [`pr-checks.yml`](../workflows/pr-checks.yml) запускается на каждый PR:

- **Tests** — по списку изменённых файлов определяются затронутые библиотеки
  ([`changed_labs.py`](../scripts/changed_labs.py)); для каждой собираются и запускаются её тесты.
  Изменение общего кода (`common/`, `allocator/allocator/`, `associative_container/include/`,
  корневого `CMakeLists.txt`) запускает тесты всех зависящих библиотек. Если PR не трогает
  ни одну библиотеку, проверка проходит без запуска тестов.
- **Lint** — clang-tidy по изменённым `.h`/`.cpp` файлам (кроме `tests/`),
  правила — в [`.clang-tidy`](../../.clang-tidy).

Запустить то же самое локально:

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
python3 .github/scripts/changed_labs.py --base origin/master   # какие тесты затронуты
cmake --build build && ctest --test-dir build --output-on-failure
python3 .github/scripts/lint.py --base origin/master            # линтер
```

Workflow [`master-guard.yml`](../workflows/master-guard.yml) дополнительно помечает красным
коммит в `master`, если он попал туда не через PR.

## Как подтягивать обновления из основного репозитория

Кнопка *Sync fork* делает прямой пуш в `master`, поэтому с включённой защитой она не сработает.
Вместо неё создайте в своём форке PR: base — `ваш-форк:master`,
head — `DesCaldnd/FIIT_SP:master` (*Pull requests → New pull request → compare across forks*).
Для таких PR тесты не запускаются. Если возник конфликт — смержите `DesCaldnd/FIIT_SP:master`
в отдельную ветку, разрешите конфликт и откройте PR из неё.
