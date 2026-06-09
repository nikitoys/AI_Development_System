# AI Development System

Языки: [English](README.md) | [Русский](README.ru.md)

Статус: Draft
Версия: v0.32.0

Этот репозиторий содержит AI Development System: операционную модель для разработки проектов через AI-роли, документацию, lifecycle governance, генерацию промптов, выполнение задач через Codex, review и контролируемую эволюцию системы.

Это не обычный application repository. Основной источник истины находится в `/ai-system`.

Источник версии: текущая версия AI_Development_System определяется верхней записью в `/ai-system/system-changelog.md`. README-файлы только отражают эту версию и не должны указывать более новую или отличающуюся версию.

Проверки целостности документации можно запустить командой:

```bash
python3 scripts/check-docs-integrity.py
```

Базовые правила безопасности и privacy/data handling описаны в `/ai-system/security-policy.md` и `/ai-system/privacy-data-handling-policy.md`.

Machine-checkable specs для стабильных системных сущностей находятся в `/spec`.

SOP и agent planning specs являются derived machine-checkable inventory/contract files. Markdown остаётся operational source of truth, а specs не разрешают runtime behavior, automatic execution, merge или acceptance.

Минимальный dry-run helper для foldered bootstrap/update находится в `scripts/foldered-control-mvp.py`.

Dry-run agent planning checks можно запускать через `scripts/agent-plan-mvp.py`.

План SOP и optional multi-agent implementation зафиксирован в `/ai-system/evolution/sop-multi-agent-implementation-plan.md`.

SOP Model описан в `/ai-system/sop-model.md`. SOP - это governance procedure, а не разрешение на automatic execution или automatic acceptance.

Agent Work Package standard описан в `/ai-system/agent-work-package.md`. Agent Work Packages - это bounded planning artifacts, а не разрешение на parallel execution.

Multi-Agent Planning workflow описан в `/ai-system/multi-agent-planning.md`. Это planning-only workflow, который не разрешает execution или parallel execution.

Parallel Execution Policy описан в `/ai-system/parallel-execution-policy.md`. Parallel execution является opt-in, требует Human Owner approval и не разрешает automatic execution, merge или acceptance.

Agent Result Intake и Integration Review описаны в `/ai-system/agent-result-intake.md` и `/ai-system/integration-review.md`. Они проверяют results перед review, QA и Human Owner acceptance, но не разрешают automatic execution, merge или acceptance.

Foldered `AI_PROJECT` templates теперь включают agent planning files для plans, packages, locks, results и metrics. Это planning records only, они не разрешают execution, parallel execution, merge или acceptance.

Golden project содержит заполненный non-runtime multi-agent planning example для Task Tracker в `examples/golden-project/`.

SOP / optional multi-agent pilot validation record находится в `/ai-system/evolution/sop-multi-agent-pilot-validation.md`.

## Кратко

Этот репозиторий описывает документированную систему разработки с помощью AI:

```text
Human Owner задаёт направление и утверждает решения.
ChatGPT Orchestrator маршрутизирует работу, готовит промпты и проверяет результаты.
AI Roles специализируются по зонам ответственности.
Codex Executor меняет файлы репозитория только в утверждённом scope.
Documentation хранит правила, решения, lifecycles и историю.
```

## Как движется работа

```text
Идея
-> Уточнение
-> Задача или change proposal
-> Prompt package
-> Human approval
-> Codex execution
-> Review
-> QA
-> Human acceptance
-> Documentation update
-> Done
```

## С чего начать

- `/ai-system/README.md` - главный индекс AI Development System.
- `/ai-system/owner-guide.md` - как Human Owner работает с системой.
- `/ai-system/operating-model.md` - что реализовано и как устроена система.
- `/ai-system/system-schemes.md` - компактные текстовые схемы ролей, документов и процесса.
- `/spec/README.md` - machine-checkable spec layer для roles, modes, verification modes и lifecycle states.

Готовый пример для старта:

- `examples/golden-project/` — полностью заполненный foldered пример для Task Tracker.

Минимальные dry-run команды:

```bash
python3 scripts/foldered-control-mvp.py bootstrap --project-root /path/to/project
python3 scripts/foldered-control-mvp.py update --project-root /path/to/project
```

## Назначение

Система помогает Human Owner работать с ChatGPT и Codex через явные роли, режимы, промпты, правила review и change governance.

Основная идея:

```text
Human Owner controls.
ChatGPT Orchestrator routes.
AI roles specialize.
Codex executes scoped repository changes.
Documentation records decisions.
```

## Текущие возможности

- Режимы взаимодействия: Free, System, Prompt, Codex, Review, Evolution и Dry Run.
- Ролевая модель для product, design, management, implementation, quality, documentation и system evolution.
- Формат Codex prompt package со scope, allowed files, forbidden actions и acceptance criteria.
- Review process с уровнями severity и decision keywords Human Owner.
- Lifecycle governance для управляемых сущностей системы.
- Language and localization policy для пользовательских ответов и generated prompts.
- Контролируемая эволюция системы через improvement log, AICP и changelog.

## Основные документы

- `/ai-system/README.md` - индекс AI Development System.
- `/ai-system/owner-guide.md` - как Human Owner взаимодействует с системой.
- `/ai-system/interaction-modes.md` - поддерживаемые режимы и routing rules.
- `/ai-system/operating-model.md` - реализованные, частичные и отсутствующие области системы.
- `/ai-system/system-structure.md` - структура ролей и слоев системы.
- `/ai-system/roles.md` - реестр AI-ролей.
- `/ai-system/rules.md` - глобальные правила системы.
- `/ai-system/prompt-lifecycle.md` - lifecycle создания, review и выполнения промптов.
- `/ai-system/task-format.md` - стандартный формат задач.
- `/ai-system/review-process.md` - процесс review и QA.
- `/ai-system/change-process.md` - процесс контролируемой эволюции.
- `/ai-system/lifecycle-governance.md` - общие lifecycle rules.
- `/ai-system/language-policy.md` - правила языка и локализации.
- `/ai-system/system-changelog.md` - история версий системы.
- `/ai-system/improvement-log.md` - замеченные process problems и improvement ideas.

## Режимы взаимодействия

Используй явные маркеры, когда нужна точность:

```text
[FREE]       ordinary explanation or discussion
[SYSTEM]     process through AI Development System
[PROMPT]     generate a prompt artifact for review
[CODEX]      prepare a Codex-ready prompt package
[REVIEW]     review Codex output
[EVOLUTION]  analyze or change the AI Development System
[DRY-RUN]    simulate without applying
```

Если маркер не указан, ChatGPT Orchestrator определяет режим по запросу.

Работа, влияющая на репозиторий, должна проходить через AI Development System process и указывать:

```text
Active Role:
Active Stage:
Active Document:
Expected Result:
```

## Language Policy

Ответы для Human Owner по умолчанию должны быть на языке Human Owner.

Системные документы и control structures по умолчанию остаются на английском:

- mode markers, например `[SYSTEM]` и `[CODEX]`;
- prompt fields, например `Scope`, `Out of Scope` и `Acceptance Criteria`;
- decision keywords, например `APPROVED`, `REWORK`, `REJECTED`, `DEFERRED` и `EXPERIMENT`;
- file paths, task IDs, branch names и command names.

Generated Codex prompts обычно должны быть English или Hybrid: стабильная английская структура с локализованными пояснениями, когда это полезно.

## Standard Workflow

```text
Human intent
-> ChatGPT Orchestrator classifies mode
-> active role and source documents are selected
-> prompt, task, review or system change is prepared
-> Human Owner approves or requests rework
-> Codex applies approved repository changes when needed
-> result is reviewed
-> changelog or documentation is updated when required
```

## Решения Human Owner

Используй эти decision words:

```text
APPROVED   accept result
REWORK     request changes
REJECTED   reject result
DEFERRED   postpone decision
EXPERIMENT test temporarily
```

AI может рекомендовать решение, но решение принимает Human Owner.

## Модель репозитория

```text
/ai-system   # AI Development System rules, roles, workflow and governance
/docs        # product documentation when a product project exists
README.md    # repository entrypoint in English
README.ru.md # Russian repository entrypoint
AGENTS.md    # instructions for future AI sessions
```

Legacy operator-loop files may exist, но `/ai-system` является текущим primary source of truth.

## Минимальные правила безопасности

- Не менять файлы репозитория, если Human Owner явно не попросил repository change или Codex execution task.
- Не рассматривать AI Development System evolution как обычный разговор.
- Не генерировать Codex prompts без mode markers и execution boundaries.
- Не принимать Codex output автоматически без review.
- Не смешивать unrelated system, product, implementation и documentation changes без явного approval.



## 1. Ролевая схема
Human Owner
│
│ задаёт направление
│ принимает финальные решения
│ утверждает результат
│
▼
ChatGPT Orchestrator
│
│ понимает запрос человека
│ выбирает нужную роль
│ готовит задачи и промпты
│ проверяет результат Codex
│ возвращает решение человеку
│
├── Product Owner AI
│   └── отвечает за ценность продукта, MVP, аудиторию, цели
│
├── Business Analyst AI
│   └── превращает идею в требования, user stories, acceptance criteria
│
├── System Architect AI
│   └── проектирует архитектуру, API, модули, БД, технические ограничения
│
├── UX/UI Designer AI
│   └── описывает экраны, user flows, состояния интерфейса
│
├── Project Manager AI
│   └── ведёт процесс, backlog, порядок задач, риски и блокеры
│
├── Backend Developer AI
│   └── готовит backend-задачи для реализации
│
├── Frontend Developer AI
│   └── готовит frontend-задачи для реализации
│
├── DevOps Engineer AI
│   └── готовит infra/deploy/Docker/CI/CD задачи
│
├── Code Reviewer AI
│   └── проверяет код, архитектуру, безопасность, scope и качество
│
├── QA Engineer AI
│   └── проверяет acceptance criteria, сценарии, edge cases, регрессии
│
├── Technical Writer AI
│   └── обновляет README, docs, changelog, onboarding
│
└── AI System Maintainer
    └── развивает саму AI Development System

Codex Executor
│
│ не принимает решений
│ не меняет scope
│ не придумывает продукт
│
└── выполняет только утверждённые задачи в репозитории

Коротко:

Human Owner решает
ChatGPT Orchestrator управляет
AI Roles думают и проверяют
Codex Executor меняет файлы
Documentation фиксирует правду

## 2. Документная схема
Repository
│
├── /ai-system
│   │
│   ├── system-prompt.md
│   │   └── главный управляющий промпт системы
│   │
│   ├── roles.md
│   │   └── кто за что отвечает
│   │
│   ├── workflow.md
│   │   └── общий путь разработки
│   │
│   ├── rules.md
│   │   └── глобальные ограничения и правила
│   │
│   ├── task-format.md
│   │   └── как должна выглядеть задача
│   │
│   ├── prompt-lifecycle.md
│   │   └── как готовить промпты для Codex
│   │
│   ├── lifecycle-governance.md
│   │   └── общие правила для всех lifecycle-документов
│   │
│   ├── task-lifecycle.md
│   │   └── как живёт задача
│   │
│   ├── codex-lifecycle.md
│   │   └── как запускается и проверяется Codex
│   │
│   ├── review-process.md
│   │   └── типы review, severity, формат review report
│   │
│   ├── review-lifecycle.md
│   │   └── состояния review, re-review, closure
│   │
│   ├── qa-lifecycle.md
│   │   └── как проходит QA и regression checks
│   │
│   ├── decision-lifecycle.md
│   │   └── как принимаются и фиксируются решения
│   │
│   ├── change-lifecycle.md
│   │   └── как меняется сама AI Development System
│   │
│   ├── knowledge-lifecycle.md
│   │   └── как ошибки и опыт превращаются в знания
│   │
│   ├── experiment-lifecycle.md
│   │   └── как безопасно тестировать временные изменения
│   │
│   ├── improvement-lifecycle.md
│   │   └── как обрабатывать идеи улучшений
│   │
│   ├── improvement-log.md
│   │   └── журнал замечаний и идей
│   │
│   └── system-changelog.md
│       └── история изменений AI Development System
│
├── /docs
│   │
│   ├── product-vision.md
│   │   └── зачем продукт нужен
│   │
│   ├── prd.md
│   │   └── что должен делать продукт
│   │
│   ├── architecture.md
│   │   └── как продукт технически устроен
│   │
│   ├── api.md
│   │   └── контракты API
│   │
│   ├── ux.md
│   │   └── пользовательские сценарии и интерфейсы
│   │
│   └── backlog.md
│       └── список задач
│
├── /backend
│   └── backend-код
│
├── /frontend
│   └── frontend-код
│
└── /infra
    └── инфраструктура и деплой

Коротко:

/ai-system отвечает за правила разработки
/docs отвечает за продукт
/backend /frontend /infra содержат реализацию

## 3. Процессная схема
1. Product Discovery
   │
   │ Владелец: Product Owner AI
   │ Результат: Product Vision
   │ Смысл: понять, что строим и зачем
   ▼

2. Requirements
   │
   │ Владелец: Business Analyst AI
   │ Результат: PRD, user stories, acceptance criteria
   │ Смысл: превратить идею в требования
   ▼

3. Architecture
   │
   │ Владелец: System Architect AI
   │ Результат: architecture.md, api.md, database schema
   │ Смысл: понять, как это будет устроено технически
   ▼

4. UX Design
   │
   │ Владелец: UX/UI Designer AI
   │ Результат: UX specification
   │ Смысл: описать экраны, состояния и поведение пользователя
   ▼

5. Planning
   │
   │ Владелец: Project Manager AI
   │ Результат: backlog task
   │ Смысл: превратить документы в конкретную задачу
   ▼

6. Prompt Preparation
   │
   │ Владелец: ChatGPT Orchestrator
   │ Результат: Codex prompt package
   │ Смысл: подготовить безопасный и ограниченный промпт
   ▼

7. Human Approval
   │
   │ Владелец: Human Owner
   │ Результат: разрешение на выполнение
   │ Смысл: человек подтверждает, что Codex можно запускать
   ▼

8. Implementation
   │
   │ Исполнитель: Codex Executor
   │ Результат: изменённые файлы, summary, checks, errors
   │ Смысл: Codex выполняет задачу в рамках scope
   ▼

9. Result Intake
   │
   │ Владелец: ChatGPT Orchestrator
   │ Результат: первичная проверка вывода Codex
   │ Смысл: понять, можно ли отправлять результат на review
   ▼

10. Review
    │
    │ Владелец: Code Reviewer AI
    │ Результат: review report
    │ Смысл: проверить scope, качество, безопасность, архитектуру
    │
    ├── Если Critical issue
    │   └── задача возвращается на rework
    │
    ├── Если Major issue
    │   └── исправить или получить явное решение Human Owner
    │
    └── Если всё нормально
        ▼

11. QA
    │
    │ Владелец: QA Engineer AI
    │ Результат: QA report
    │ Смысл: проверить acceptance criteria и пользовательские сценарии
    │
    ├── Если найдены дефекты
    │   └── задача возвращается на rework
    │
    └── Если QA пройден
        ▼

12. Human Acceptance
    │
    │ Владелец: Human Owner
    │ Результат: принято / отклонено / отправлено на доработку
    │ Смысл: финальное решение принимает человек
    ▼

13. Documentation Update
    │
    │ Владелец: Technical Writer AI
    │ Результат: README, docs, changelog
    │ Смысл: документация приводится в соответствие с изменениями
    ▼

14. Done

Коротко:

Идея
→ требования
→ архитектура
→ UX
→ задача
→ промпт
→ Codex
→ review
→ QA
→ решение человека
→ обновление документации
→ Done
