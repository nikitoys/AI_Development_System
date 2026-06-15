Status: Legacy Concept Baseline
Version: v0.1.0

This document is a historical/conceptual baseline for AI_Development_System evolution.
It is not the current source of truth.
Current authoritative evolution documents live in:
- ai-system/evolution/roadmap.md
- ai-system/evolution/owner-evolution-plan.md
- ai-system/evolution/owner-plan-intake.md
- ai-system/evolution/evolution-backlog.md
- ai-system/evolution/evolution-policy.md

# Концепция эволюции AI Development System

Status: Draft  
Purpose: смысловая основа для дальнейшей переработки /ai-system

## 1. Назначение

AI Development System нужен не как большой универсальный промпт, а как
управляемая система разработки приложения с помощью ИИ.

Система должна помогать владельцу проекта:

- превращать идею продукта в документы;
- разбирать работу на маленькие задачи;
- передавать в Codex только подготовленные и ограниченные задачи;
- проверять результат через review и QA;
- фиксировать решения в документации;
- улучшать сам процесс разработки без хаотичных изменений.

Главная мысль:

    Человек принимает решения.
    ChatGPT организует работу.
    AI-роли специализируются.
    Codex меняет файлы.
    Документация хранит правду.

## 2. Почему система нужна

Один длинный запрос к ИИ плохо контролирует разработку:

- роли смешиваются;
- требования, архитектура и код появляются в неправильном порядке;
- ИИ начинает добавлять лишние функции;
- решения остаются только в чате;
- Codex получает слишком широкий или неясный запрос;
- review и QA легко пропускаются.

Система решает это через разделение ответственности, документы, этапы,
ограничения и явное одобрение владельца.

## 3. Основные принципы

1. Документация является источником правды.
2. Код не пишется без понятной задачи, scope и acceptance criteria.
3. Каждая роль работает только в своей зоне ответственности.
4. Codex является исполнителем, а не владельцем продуктовых решений.
5. MVP важнее идеальной архитектуры и полноты "на будущее".
6. Любое изменение системы проходит через контролируемый evolution process.
7. Если документация и ответ ИИ конфликтуют, конфликт нужно явно разрешить.

## 4. Участники

### Human Owner

Владелец проекта и финальный источник решений.

Отвечает за:

- направление продукта;
- approval / rework / rejection;
- границы MVP;
- принятие рисков;
- разрешение на изменение AI Development System.

### ChatGPT Orchestrator

Организатор процесса.

Отвечает за:

- выбор активной роли;
- выбор этапа работы;
- определение нужного документа;
- подготовку Codex-задач;
- анализ результата Codex;
- маршрутизацию вопросов по слоям системы;
- выявление противоречий и scope creep.

### AI Roles

Специализированные роли, которые помогают создавать документы, задачи,
архитектуру, проверки и предложения.

Минимальный рабочий набор:

- Project Manager AI;
- Product Owner AI;
- Business Analyst AI;
- System Architect AI;
- Developer AI;
- QA / Reviewer AI;
- Technical Writer AI;
- AI System Maintainer.

Для больших проектов Developer AI и QA / Reviewer AI могут быть разделены:

- Backend Developer AI;
- Frontend Developer AI;
- DevOps Engineer AI;
- QA Engineer AI;
- Code Reviewer AI.

### Codex Executor

Исполнитель изменений в репозитории.

Codex должен получать:

- контекст;
- source documents;
- конкретную задачу;
- allowed files;
- out of scope;
- acceptance criteria;
- checks;
- ожидаемый формат результата.

Codex не должен самостоятельно менять продуктовый scope, архитектуру,
workflow или правила системы.

## 5. Слои системы

### Product Layer

Отвечает на вопрос: что мы строим и зачем?

Роли:

- Product Owner AI;
- Business Analyst AI.

Документы:

- Product Vision;
- PRD;
- User Stories;
- Acceptance Criteria.

### Design Layer

Отвечает на вопрос: как продукт должен работать технически и для пользователя?

Роли:

- System Architect AI;
- UX/UI Designer AI, если нужен отдельный UX-слой.

Документы:

- Architecture Document;
- API Documentation;
- Database Schema;
- UX Specification.

### Management Layer

Отвечает на вопрос: в каком порядке работать?

Роль:

- Project Manager AI.

Документы:

- Backlog;
- task plan;
- current status;
- risk list.

### Implementation Layer

Отвечает на вопрос: как превратить задачу в изменения файлов?

Роли:

- Developer AI;
- Backend Developer AI;
- Frontend Developer AI;
- DevOps Engineer AI;
- Codex Executor.

Артефакты:

- код;
- тесты;
- инструкции проверки;
- infrastructure files.

### Quality Layer

Отвечает на вопрос: можно ли принять результат?

Роли:

- QA / Reviewer AI;
- QA Engineer AI;
- Code Reviewer AI.

Артефакты:

- Review Report;
- QA Report;
- test cases;
- regression checklist.

### Documentation Layer

Отвечает на вопрос: все важное зафиксировано?

Роль:

- Technical Writer AI.

Документы:

- README;
- changelog;
- setup guide;
- project structure;
- onboarding notes.

### System Evolution Layer

Отвечает на вопрос: нужно ли менять саму систему разработки?

Роль:

- AI System Maintainer.

Артефакты:

- Improvement Log entry;
- AI System Change Proposal;
- system changelog update;
- experiment proposal;
- version impact.

## 6. Базовый workflow

    Product Discovery
    -> Requirements
    -> Architecture
    -> UX Design
    -> Planning
    -> Implementation
    -> Review
    -> QA
    -> Deployment
    -> Documentation Update

Этот workflow не обязан всегда выполняться полностью. Для маленькой задачи
можно пройти только нужные этапы, но нельзя пропускать смысловые gates:

- до реализации должна быть понятная задача;
- до задачи должны быть требования или подтвержденное решение;
- до acceptance должны быть review, QA или явное принятие риска;
- после изменения поведения документация должна быть обновлена.

## 7. Рабочий цикл задачи

    Идея
    -> Документированное требование
    -> Архитектурное или UX-решение, если нужно
    -> Backlog task
    -> Codex prompt
    -> Изменения в репозитории
    -> Review
    -> QA
    -> Approval
    -> Документация / changelog

Минимальная задача готова к Codex, когда у нее есть:

- цель;
- контекст;
- scope;
- out of scope;
- allowed files;
- acceptance criteria;
- checks;
- stop conditions.

## 8. Режимы взаимодействия

Не каждый вопрос должен включать полный system process.

### Free Mode

Используется для объяснений, обсуждений и размышлений.

Примеры:

- "Объясни, зачем нужен AI System Maintainer."
- "Чем QA отличается от Code Review?"
- "Можно ли сделать систему проще?"

Файлы не меняются.

### System Mode

Используется, когда запрос влияет на репозиторий, документы, роли, workflow,
архитектуру, правила или Codex-задачи.

Операционный ответ должен определять:

    Active Role:
    Active Stage:
    Active Document:
    Expected Result:

### Codex Mode

Используется для подготовки конкретного prompt package для Codex.

### Review Mode

Используется для проверки результата Codex.

### Evolution Mode

Используется для изменения самой AI Development System.

### Dry Run Mode

Используется для симуляции изменения без правки файлов.

## 9. Правила для Codex

Codex-задача должна быть маленькой и проверяемой.

В prompt package нужно включать:

- активную роль;
- краткий контекст;
- source documents;
- task ID или название задачи;
- allowed files;
- forbidden files;
- scope;
- out of scope;
- acceptance criteria;
- main check;
- negative checks;
- stop conditions;
- expected result format.

Codex должен вернуть:

- changed files;
- summary;
- checks run;
- failed checks, если есть;
- unresolved questions;
- diff summary.

## 10. Правила review и QA

Результат нельзя считать принятым только потому, что файлы изменены.

Review проверяет:

- соответствие задаче;
- соответствие архитектуре;
- scope creep;
- читаемость;
- безопасность;
- обработку ошибок;
- риск регрессии.

QA проверяет:

- acceptance criteria;
- positive scenarios;
- negative scenarios;
- edge cases;
- user-facing behavior;
- regression checklist.

Severity:

- Critical blocks acceptance;
- Major требует исправления или явного принятия риска;
- Minor не блокирует, но фиксируется;
- Suggestion остается опциональным.

## 11. Эволюция системы

AI Development System не должна меняться случайно.

Изменение нужно, если:

- одна и та же проблема повторяется;
- роли конфликтуют;
- Codex часто выходит за scope;
- workflow слишком тяжелый или слишком слабый;
- review пропускает важные ошибки;
- документация перестала быть источником правды;
- новые типы задач не укладываются в текущую модель.

Изменение не нужно, если:

- проблема случилась один раз;
- достаточно уточнить конкретную задачу;
- изменение добавит больше сложности, чем пользы;
- существующая роль может решить проблему малой правкой prompt или документа.

Базовый evolution flow:

    Observation
    -> Improvement Log
    -> Root Cause
    -> AI System Change Proposal
    -> Human Decision
    -> Codex Task
    -> Review
    -> System Changelog
    -> Version Update

## 12. Что уже оформлено в репозитории

Смысл этого черновика уже частично разнесен по документам:

- /ai-system/README.md - назначение системы;
- /ai-system/system-structure.md - структура ролей и слоев;
- /ai-system/roles.md - краткий реестр ролей;
- /ai-system/workflow.md - основной workflow;
- /ai-system/rules.md - глобальные правила;
- /ai-system/task-format.md - формат задачи;
- /ai-system/review-process.md - review и QA;
- /ai-system/change-process.md - evolution process;
- /ai-system/interaction-modes.md - режимы взаимодействия;
- /ai-system/role-lifecycle.md - изменение ролей;
- /ai-system/operating-model.md - карта реализованных и отсутствующих механизмов.

## 13. Что стоит сделать дальше

Этот файл больше не должен быть единственным источником системы. Его лучше
использовать как смысловую карту для следующих задач:

1. Сверить /ai-system/roles.md с минимальным набором ролей.
2. Уточнить, когда использовать Developer AI, а когда split на backend,
   frontend и DevOps.
3. Создать недостающие lifecycle-документы из operating-model.md.
4. Синхронизировать system-prompt.md с interaction modes и role lifecycle.
5. Добавить короткие примеры Codex prompt package.
6. Заполнить PROJECT_GOAL.md, CODEX_PLAN.md и checks для этого репозитория.

## 14. Итоговая формула

    Не "ИИ пишет проект".

    А:

    Человек задает направление.
    Система превращает направление в документы и задачи.
    Codex выполняет маленькие проверяемые изменения.
    Review и QA удерживают качество.
    Документация сохраняет решения.
    Evolution process улучшает саму систему.
